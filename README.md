# 5-Squares
A Python / Pygame exercise to build a tiled memory game.
This game is a 5 x 5 matrix - 25 squares. We need only 24.
The middle square (200, 200) is taken out of the self.tile_list
leaving only 24 entries. However an extra number has to be added
to self.card_list after it is duplicated and shuffled so there are
25 numbers same as the numbers of squares. This is number 12 and
is never called for. The middle square has no cover and is used to signal
if the tiles are a good match or not.
