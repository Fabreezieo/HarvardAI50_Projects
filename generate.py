import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.domains:
            copy = self.domains[var].copy()
            for word in copy:
                if len(word) != var.length:

                    self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        overlap = self.crossword.overlaps[x, y]
        
        if overlap is not None:
            
            words_to_delete = set()

            for wordX in self.domains[x]:           
                
                x_overlap = wordX[overlap[0]]
                y_overlaps= {w[overlap[1]] for w in self.domains[y]}

                if x_overlap not in y_overlaps:
                    words_to_delete.add(wordX)
                    revised = True
            
            for word in words_to_delete:
                self.domains[x].remove(word)
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            arcs = []
            
            for x in self.crossword.overlaps:
                if self.crossword.overlaps[x] is None:
                    continue
                else:
                    arcs.append(x)
        
        while len(arcs) != 0:
            arc = arcs.pop()
            v1, v2 = arc[0], arc[1]

            if self.revise(v1, v2):
                if len(self.domains[v1]) == 0:
                    return False

                c = self.crossword.neighbors(v1).copy()
                c.remove(v2)
                for v in c:
                    if self.crossword.overlaps[v1, v] is None:
                        continue
                    
                    else: 
                        arcs.append((v, v1))
        return True
            


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if len(assignment) == len(self.domains):
            return True
        return False

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for var1, word1 in assignment.items():
            for var2, word2 in assignment.items():
                if var1 != var2:
                    if word1 == word2:
                        return False
                    if (var1, var2) in self.crossword.overlaps and self.crossword.overlaps[var1, var2]:
                        overlap = self.crossword.overlaps[var1, var2]
                        if word1[overlap[0]] != word2[overlap[1]]:
                            return False
        return True


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """        
        
        words_excluded = {
            word : 0 for word in self.domains[var]
        }

        neighbors = self.crossword.neighbors(var) - assignment.keys()

        for word_var in self.domains[var]:

            for neighbor in (neighbors - assignment.keys()):

                overlap = self.crossword.overlaps[var, neighbor]

                for word_y in self.domains[neighbor]:

                    if word_var[overlap[0]] != word_y[overlap[1]]:
                        words_excluded[word_var] += 1

        sorted_list = sorted(words_excluded.items(), key= lambda x: x[1])
        return [x[0] for x in sorted_list]


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        possible = list(self.domains.keys() - assignment.keys())

        sorted(possible, key= lambda x: len(self.domains[x]))

        if len(possible) > 1:
            
            if len(self.domains[possible[0]]) == len(self.domains[possible[1]]):
                
                if len(self.crossword.neighbors(possible[0])) > len(self.crossword.neighbors(possible[1])):
                    return possible.pop(1)

        return possible.pop(0)

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        
        var = self.select_unassigned_variable(assignment)

        for x in self.order_domain_values(var, assignment):
            new_assignment = assignment.copy()
            new_assignment[var] = x
            if self.consistent(new_assignment):
                result = self.backtrack(new_assignment)
                if result is not None:
                    return result
        
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
