#!/usr/bin/env python
# -*- coding: utf-8 -*-
from enum import Enum
from typing import Dict, Any, Set, Tuple

import sys
import os
import re

from pathlib import Path

sys.path.append(str(Path(__file__).absolute().resolve().parent.parent.parent.joinpath(Path('bindings/python/src'))))

from lxml import etree as ET

from mercury_nn import filter_validation
from mercury_nn import manifest_validation

from mercury_nn.manifest_validation import validateManifest, ManifestValidationResult

from mercury_nn.specification.load_valid_usages import loadValidUsage
from mercury_nn.specification.load_filter_match_failure_specs import loadFilterMatchFailureSpecs

from mercury_nn.specification.interface import FilterSyntaxInvalidityType, ManifestSyntaxInvalidityType, FilterMatchFailureType
from mercury_nn.config import Config

from mercury_nn.filtering import Filter, matchFilter, FilterMatchResult

import argparse


class CommandTypes:
    VALIDATE_MANIFEST = "validate-manifest"
    VALIDATE_FILTER = "validate-filter"


# argparse
parser = argparse.ArgumentParser(description="Mercury Command-Line Utility")

subparsers = parser.add_subparsers(dest='command')

manifest_validation_subparser = subparsers.add_parser(
    CommandTypes.VALIDATE_MANIFEST,
    help='Validates a manifest.'
)

manifest_validation_subparser.add_argument('manifest_file', type=str)

filter_validation_subparser = subparsers.add_parser(
    CommandTypes.VALIDATE_FILTER,
    help='Validates a filter.'
)

filter_validation_subparser.add_argument('filter_file', type=str)

args = parser.parse_args()


# load valid usages
filter_syntax_valid_usages = loadValidUsage(filepath=Config.filterSyntaxValidUsageFile)
manifest_syntax_valid_usages = loadValidUsage(filepath=Config.manifestSyntaxValidUsageFile)

def get_attributes(cls: type) -> Dict[str, Any]:
    return {k: getattr(cls, k) for k in dir(cls) if not k.startswith('__') and not k.endswith('__')}

# validation
assert set(get_attributes(FilterSyntaxInvalidityType).values()) == set(filter_syntax_valid_usages.keys())
assert set(get_attributes(ManifestSyntaxInvalidityType).values()) == set(manifest_syntax_valid_usages.keys())

# load filter match failure specs
filter_match_failure_specs = loadFilterMatchFailureSpecs(filepath=Config.filterMatchFailureSpecsFile)

# validation
assert set(get_attributes(FilterMatchFailureType).values()) == set(filter_match_failure_specs.keys())


def _transform_text(text: str) -> str:
    """Removes leading & trailing whitespaces & line breaks.
    Also removes indentation.
    Adjacent lines not separated by empty lines are joined into a single line,
    where the line break is replaced by a whitespace character.

    Multiple consecutive empty lines are collapsed to a single empty line.

    Args:
        text (str): The text to transform.

    Returns:
        str: Transformed text.
    """
    
    # remove leading & trailing whitespaces & line breaks
    text = re.sub(r'^\s+', '', text)
    text = re.sub(r'\s+$', '', text)

    # remove indentation
    lines = text.split(os.linesep)
    for i, line in enumerate(lines):
        lines[i] = re.sub(r'^\s+', '', line)
    
    # collapse empty lines & line breaks
    current_line = ''
    new_lines = []
    for line in lines:
        if line == '':
            if current_line != '':
                new_lines.append(current_line)
            current_line = ''
        else:
            current_line += ' ' + line
    
    if current_line != '':
        new_lines.append(current_line)
    
    return (os.linesep * 2).join(new_lines)
    

def main(args) -> int:
    def _transform(text: str) -> str:
        return os.linesep.join(' ' * 4 + line for line in _transform_text(text).split(os.linesep))
    
    match args.command:
        case CommandTypes.VALIDATE_MANIFEST:
            # load manifest
            try:
                with open(args.manifest_file, 'r') as f:
                    manifest_element = ET.parse(f)
                    manifest_element = manifest_element.getroot()
            except FileNotFoundError:
                print(f'File not found: {args.manifest_file}', file=sys.stderr)
                return 1
            except ET.ParseError:
                print(f'Manifest is not a valid XML document!', file=sys.stderr)
                return 1

            # validate manifest
            result = validateManifest(manifest_element)

            if result.isValid:
                print('Manifest is valid.')
                
                return 0
            
            match result.invalidityInfo.invalidityType:
                case ManifestValidationResult.InvalidityInfo.InvalidityType.INVALID_SYNTAX:
                    info: manifest_validation.SyntaxValidationResult.InvalidityInfo = result.invalidityInfo.info
                    line_pos = info.invalidityPosition.line
                    invalidity_type = info.invalidityType
                    vu_entry = manifest_syntax_valid_usages[invalidity_type]
                    vu_name = vu_entry.name
                    vu_description = vu_entry.description
                    
                    print(f'Syntactical valid usage violation detected at line {line_pos}: {vu_name}', file=sys.stderr)
                    print(f'Description of valid usage:\n\n{_transform(vu_description)}', file=sys.stderr)
                    
                case ManifestValidationResult.InvalidityInfo.InvalidityType.FAILED_BASE_MODEL_FILTER_MATCH:
                    info: FilterMatchResult.FailureInfo = result.invalidityInfo.info
                    # we know that the base model filter does not have tags
                    filterer_line, filteree_line, _ = info.failurePosition.filtererLine, info.failurePosition.filtereeLine, info.failurePosition.tagStack
                    failure_entry = filter_match_failure_specs[info.failureType]
                    failure_name = failure_entry.name
                    failure_description = failure_entry.description

                    print(f'Match failure detected when matching the manifest against the base model filter, at line {filterer_line} (base model filter), {filteree_line} (manifest): {failure_name}', file=sys.stderr)
                    print(f'Description of match failure:\n\n{_transform(failure_description)}', file=sys.stderr)

                case ManifestValidationResult.InvalidityInfo.InvalidityType.UNKNOWN_TAGS:
                    info: Set[str] = result.invalidityInfo.info
                    
                    print(f'The following tags referenced in the manifest are unknown:\n', file=sys.stderr)
                    print('\n'.join(' ' * 4 + name for name in info))
                    
                case ManifestValidationResult.InvalidityInfo.InvalidityType.UNMATCHED_TAG:
                    tag, info = result.invalidityInfo.info
                    filterer_line, filteree_line, stack = info.failurePosition.filtererLine, info.failurePosition.filtereeLine, info.failurePosition.tagStack
                    failure_entry = filter_match_failure_specs[info.failureType]
                    failure_name = failure_entry.name
                    failure_description = failure_entry.description
                    
                    final_tag = tag if len(stack) == 0 else stack[-1]

                    print(f'Match failure detected when matching a tag present in the manifest (named "{tag}") against the manifest.', file=sys.stderr)
                    print(f'The match failure named "{failure_name}" occurred at line {filterer_line} ("{final_tag}"), {filteree_line} (manifest).', file=sys.stderr)
                    if len(stack) > 0:
                        print(f'The tag named "{final_tag}" was being matched because the following tag-inclusion relationship exists ("<a> -> <b>" means "tag <a> includes tag <b>"):', file=sys.stderr)
                        print(' ' * 4 + ' -> '.join(['(manifest)', tag] + stack), file=sys.stderr)
                    
                    print(f'Description of the match failure "{failure_name}":\n\n{_transform(failure_description)}', file=sys.stderr)
            
            return 1

        case CommandTypes.VALIDATE_FILTER:
            try:
                with open(args.filter_file, 'r') as f:
                    xml_element = ET.parse(f)
                    xml_element = xml_element.getroot()
            except FileNotFoundError:
                print(f'File not found: {args.filter_file}', file=sys.stderr)
                
                return 1
            except ET.ParseError:
                print(f'Filter is not a valid XML document!', file=sys.stderr)
                return 1
                    
            validation_result = filter_validation.checkFilterSyntax(xml_element)

            if validation_result.isValid:
                print('Filter is valid.')
                
                return 0
            else:
                invalidity_info = validation_result.invalidityInfo
                
                print(f'Valid usage violation detected at line {invalidity_info.invalidityPosition.line}: {invalidity_info.invalidityType}', file=sys.stderr)
                print(f'Description of valid usage: {filter_syntax_valid_usages[invalidity_info.invalidityType].description}', file=sys.stderr)

                return 1
                
        case _:
            print(f'Invalid command: {args.command}', file=sys.stderr)
            
            return 1


if __name__ == '__main__':
    return_code = main(args)
    exit(return_code)
