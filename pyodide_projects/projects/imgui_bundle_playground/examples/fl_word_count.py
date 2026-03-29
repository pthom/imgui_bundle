"""The word count problem.

This is a simple example that provides a solution to a famous coding challenge:
    > Read a file of text, determine the n most frequently used words,
    > and print out a sorted list of those words along with their frequencies.

References:
* https://rosettacode.org/wiki/Word_frequency#C.2B.2B

    Doug McIlroy's solution is a classic example of the Unix philosophy:

    ```bash
    tr -cs A-Za-z '\n' |     # Replace non-alphabetic characters with newlines
    tr A-Z a-z |             # Convert to lowercase
    sort |                   # Sort the words
    uniq -c |                # Count the number of times each word appears
    sort -rn |               # Sort by frequency
    sed ${1}q                # Print the first n lines
    ```

Here, the solution is implemented as a composition of functions, each of which is a step in the solution.
With fiatlight, we can easily examine the intermediate results of each step.
"""

from typing import List, Tuple
import fiatlight as fl


def text_source() -> str:
    """Return the text to be analyzed."""
    # Here, we simply return the __doc__ string of this file, i.e., the long explanation at the beginning of this file.
    return __doc__

    # We could also read a file from the web
    # (warning, when using Pyodide, security restrictions may apply: a web client cannot fetch resources
    # from a different domain than the one it was loaded from, unless the server allows it)
    #
    # import requests
    # hamlet_url = "http://localhost:8005/examples/hamlet.txt"
    # response = requests.get(hamlet_url)
    # return response.text


def str_lower(text: str) -> str:
    return text.lower()

def remove_non_letters(text: str) -> str:
    return "".join(c if c.isalpha() else " " for c in text)

def split_words(text: str) -> List[str]:
    return text.split()

def sort_words(words: List[str]) -> List[str]:
    return sorted(words)


# WordWithCount is a tuple of a word and the number of times it appears.
WordWithCount = Tuple[str, int]


def run_length_encode(input_list: List[str]) -> List[WordWithCount]:
    """Run-length encode a list of words:

    Count the number of times each word appears in the list. The input list must be sorted.
    Returns a list of tuples, where each tuple contains a word and the number of times it appears.
    """
    r: List[WordWithCount] = []

    for i in range(len(input_list)):
        current = input_list[i]
        previous = input_list[i - 1] if i > 0 else None
        if current == previous:
            previous_count = r[-1][1]
            r[-1] = (current, previous_count + 1)
        else:
            r.append((current, 1))
    return r


def filter_out_short_words(words: List[str], min_length: int = 4) -> List[str]:
    """Filter out words that are shorter than a given length."""
    return list(filter(lambda word: len(word) >= min_length, words))


@fl.with_fiat_attributes(label="Most common words")
def sort_word_with_counts(words: List[WordWithCount]) -> List[WordWithCount]:
    """Sort a list of words by frequency, in descending order,
    so that the most frequent words come first."""
    r = sorted(words, key=lambda w: w[1], reverse=True)
    return r


def main() -> None:
    fl.run(
        [
            text_source,
            str_lower,
            remove_non_letters,
            split_words,
            filter_out_short_words,
            sort_words,
            run_length_encode,
            sort_word_with_counts,
        ],
        params=fl.FiatRunParams(app_name="demo_word_count", theme=fl.ImGuiTheme_.white_is_white),
    )


if __name__ == "__main__":
    main()
