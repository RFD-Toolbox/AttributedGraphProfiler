from typing import List


class ArraySplitter:
    @staticmethod
    def consecutive_subsequences(values: list) -> List[list]:
        values = sorted(values)
        result = []
        sequence = []

        for index, number in enumerate(values):
            if not sequence:
                sequence.append(number)
            elif number == sequence[-1] + 1:  # Consecutive values
                sequence.append(number)

                if index == len(values) - 1:
                    result.append(sequence)

            else:  # First not consecutive value
                result.append(sequence)
                sequence = [number]

        return result
