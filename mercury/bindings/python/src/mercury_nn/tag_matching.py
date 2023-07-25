from typing import Set, List
import re

from .specification.constants import (
    CONDENSED_TAGS_NAMESPACE_DELIMITER,
    CONDENSED_TAGS_CONCATENATION_DELIMITER,
    CONDENSED_TAGS_IGNORED_CHARS,
    CONDENSED_TAGS_NESTED_FIELD_DELIMITER_END,
    CONDENSED_TAGS_NESTED_FIELD_DELIMITER_START,
    CONDENSED_TAGS_PARALLEL_SEPARATOR,
    TAG_COMPONENT_NAME_REGULAR_EXPRESSION
)


class InvalidCondensedTagsException(Exception):
    pass


def _segmentContent(sequence: str, startDelimiter: str, endDelimiter: str) -> str | None:
    """Segments content between start and end delimiters.
    The starting delimiter and all content before it are assumed to have been removed.

    Args:
        sequence (str): The sequence to search.
        startDelimiter (str): The delimiter that starts a field. E.g., '{', '(', '['.
        endDelimiter (str): The delimiter that ends a field. E.g., '}', ')', ']'.
    
    Returns:
        str | None: The content between start and end delimiters, or None if the function fails because of unmatched delimiters.
    
    Examples
    ========
    
    >>> segmentContent('{{tag1, tag2}}}}', '{{', '}}')
    '{{tag1, tag2}}'
    """
    
    tokens = [sequence]
    
    # break into tokens
    for seq in {startDelimiter, endDelimiter}:
        # split each large token into smaller tokens
        for i in range(len(tokens)):
            tokens[i] = tokens[i].split(seq)

        # concatenate all splitted tokens
        new_tokens = []
        for token_set in tokens:
            new_tokens += token_set
        
        tokens = new_tokens
    
    # parse
    currentStack = []
    for i, token in enumerate(tokens):
        if token == startDelimiter:
            currentStack.append(token)
        elif token == endDelimiter:
            if len(currentStack) == 0:
                return ''.join(tokens[:i])
            else:
                currentStack.pop()
    
    return None


def parseCondensedTags(condensedTags: str) -> Set[str]:
    """Breaks condensed tag collection into individual tags.

    Args:
        condensedTags (str): The condensed tags.
    
    Returns:
        Set[str]: The individual tags.
    
    Raises:
        InvalidCondensedTagsException: If the condensed tags are invalid (e.g., unmatched delimiters, etc.).
        
    Examples
    ========

    >>> parseCondensedTags('tag1')
    {'tag1'}
    
    >>> parseCondensedTags('{tag1, tag2}')
    {'tag1', 'tag2'}

    >>> parseCondensedTags('{tag1.tag2.tag3.tag4.tag5}')
    {'tag1', 'tag1::tag2', 'tag1::tag2::tag3', 'tag1::tag2::tag3::tag4', 'tag1::tag2::tag3::tag4::tag5'}

    >>> parseCondensedTags('tag1.tag2.{tag3.{tag6, tag7}, tag4}')
    {'tag1', 'tag1::tag2', 'tag1::tag2::tag3', 'tag1::tag2::tag3::tag6', 'tag1::tag2::tag3::tag7', 'tag1::tag2::tag4'}
    
    >>> parseCondensedTags('tag1::tag2::{tag3.{tag6, tag7}, tag4}')
    {'tag1::tag2::tag3', 'tag1::tag2::tag3::tag6', 'tag1::tag2::tag3::tag7', 'tag1::tag2::tag4'}
    """
    
    for seq in CONDENSED_TAGS_IGNORED_CHARS:
        condensedTags = condensedTags.replace(seq, '')
    
    return parseCondensedTagsNoIgnoredCharacters(condensedTags)


def parseCondensedTagsNoIgnoredCharacters(condensedTags: str) -> Set[str]:
    
    def split_with_delimiters(sequence: str, delimiters_set: Set[str]):
        tokens = [sequence]
        
        for seq in delimiters_set:
            new_tokens = []

            for token in tokens:
                sub_tokens = []
                
                while True:
                    pos = token.find(seq)
                    if pos < 0:
                        if token != '':
                            sub_tokens.append(token)
                        break

                    sub_tokens += [token[:pos], seq]
                    token = token[pos + len(seq):]
                
                new_tokens += sub_tokens
            
            tokens = new_tokens
        
        return tokens
    
    # break into tokens: O(n)
    tokens = split_with_delimiters(condensedTags, {CONDENSED_TAGS_NESTED_FIELD_DELIMITER_START, CONDENSED_TAGS_NESTED_FIELD_DELIMITER_END, CONDENSED_TAGS_PARALLEL_SEPARATOR})

    # remove empty tokens
    tokens = list(filter(lambda x: x != '', tokens))
    
    # parse: O(n)
    def parse_tokens(tokens: List[str]) -> List[str]:
        if len(tokens) == 0:
            return []
        
        # find first component
        first_component, remainings = None, None
        nested_delimiter_stack = []
        
        for i, token in enumerate(tokens):
            if token == CONDENSED_TAGS_NESTED_FIELD_DELIMITER_START:
                nested_delimiter_stack.append(token)
            elif token == CONDENSED_TAGS_NESTED_FIELD_DELIMITER_END:
                if len(nested_delimiter_stack) == 0:
                    # unmatched delimiters
                    raise InvalidCondensedTagsException()
                
                nested_delimiter_stack.pop()
            elif token == CONDENSED_TAGS_PARALLEL_SEPARATOR:
                if len(nested_delimiter_stack) == 0:
                    # end of first component
                    first_component = tokens[:i]
                    remainings = tokens[i + 1:]
                    break
            
        if first_component is None:
            if len(nested_delimiter_stack) == 0:
                first_component = tokens.copy()
                remainings = []
            else:
                raise InvalidCondensedTagsException()
        
        if CONDENSED_TAGS_NESTED_FIELD_DELIMITER_START in first_component:
            if first_component[-1] != CONDENSED_TAGS_NESTED_FIELD_DELIMITER_END:
                # things like {a, b}::c are not allowed
                raise InvalidCondensedTagsException()
            
            # parse the content in the nested field recursively
            prefix = first_component[:first_component.index(CONDENSED_TAGS_NESTED_FIELD_DELIMITER_START)]
            sub_body = first_component[first_component.index(CONDENSED_TAGS_NESTED_FIELD_DELIMITER_START) + 1:-1]
            prefix = ''.join(prefix)
            first_component_tag_chains = [prefix + tag_chain for tag_chain in parse_tokens(sub_body)]
        else:
            first_component_tag_chains = [''.join(first_component)]
        
        # now parse the remaining tokens recursively
        remaining_tag_chains = parse_tokens(remainings)

        return first_component_tag_chains + remaining_tag_chains
    
    tag_chains = parse_tokens(tokens)
    
    def parse_tag_chain(tag_chain: str) -> Set[str]:
        if tag_chain.startswith(CONDENSED_TAGS_CONCATENATION_DELIMITER) or \
            tag_chain.endswith(CONDENSED_TAGS_CONCATENATION_DELIMITER) or \
            tag_chain.startswith(CONDENSED_TAGS_NAMESPACE_DELIMITER) or \
            tag_chain.endswith(CONDENSED_TAGS_NAMESPACE_DELIMITER):
            raise InvalidCondensedTagsException()
        
        # split: O(n)
        tokens = split_with_delimiters(tag_chain, {CONDENSED_TAGS_NAMESPACE_DELIMITER, CONDENSED_TAGS_CONCATENATION_DELIMITER})

        tags = []
        last_token = None
        prefix = []
        
        # parse: O(n)
        def is_token_regular_string(token: str | None):
            return (token is not None) and token != CONDENSED_TAGS_NAMESPACE_DELIMITER and token != CONDENSED_TAGS_CONCATENATION_DELIMITER
        for token in tokens:
            if token == CONDENSED_TAGS_NAMESPACE_DELIMITER:
                if not is_token_regular_string(last_token):
                    raise InvalidCondensedTagsException()
                
                tags.pop()
                prefix.append(last_token)
            elif token == CONDENSED_TAGS_CONCATENATION_DELIMITER:
                if not is_token_regular_string(last_token):
                    raise InvalidCondensedTagsException()
                prefix.append(last_token)
            else:
                # something like text-continuation
                # check for validity
                if re.search(TAG_COMPONENT_NAME_REGULAR_EXPRESSION, token) is None:
                    # invalid tag component
                    raise InvalidCondensedTagsException()
                
                tags.append(CONDENSED_TAGS_NAMESPACE_DELIMITER.join(prefix + [token]))
            
            last_token = token
        
        return set(tags)
    
    tags = set()
    
    for tag_chain in tag_chains:
        tags.update(parse_tag_chain(tag_chain))
    
    return tags
