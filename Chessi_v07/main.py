"""
Diese Version beinhaltet eine GUI, die leider nach 30 Tagen abläuft.
Man kann gegen eine Engine spielen, in dem man den eigenen Zug in der Form e2e4 eingibt.
Die Engine beherrscht alle Schachregeln und spielt bis zum Partieende.
In Version 5 ist eine Stellungsbewertung integriert. Außerdem wird eine mögliche Zugfolge dargestellt.
"""

import chess
import chess.engine
import PySimpleGUI as sg
from PIL import Image
from io import BytesIO

# die Pfade für die Engines
maia = "/home/harald/Entwicklung/PycharmProjects/Engines/Lc0-0.27.0"
stockfish = "/home/harald/Entwicklung/Python/Chessi/Engines/stockfish-ubuntu-x86-64-avx2"

# das engine-Objekt wird erstellt
engine = chess.engine.SimpleEngine.popen_uci(maia)

# Zeit pro Zug in Sekunden und Rechentiefe wird festgelegt
zeit = 5.0
tiefe = 20

class Chessi_v07:
    def __init__(self):
        # Erstelle das Schachbrett
        self.board = chess.Board()
        # self.selected_square = None

    # Engine führt Zug aus
    def get_move(self, window):
        result = engine.play(self.board, chess.engine.Limit(time=zeit, depth=tiefe))
        # Stellungsbewertung
        info = engine.analyse(self.board, chess.engine.Limit(time=zeit, depth=tiefe))
        window["Bewertung"].update(info["score"])
        # aktualisiere Schachbrett
        self.board.push(result.move)
        window["Züge"].update(info.get("pv"))
        if (self.board.is_checkmate()):
            window["Bewertung"].update("Schachmatt")
        elif (self.board.is_check()):
            window["Bewertung"].update("Schach")
        return result.move

    # Spieler führt Zug aus
    def human_move(self, from_square, to_square, window):
        move = chess.Move(from_square, to_square)
        if move in self.board.legal_moves:
            # aktualisiere Schachbrett
            self.board.push(move)
            info = engine.analyse(self.board, chess.engine.Limit(time=zeit, depth=tiefe))
            window["Bewertung"].update(info["score"])
            if (self.board.is_checkmate()):
                window["Bewertung"].update("Schachmatt")
            elif (self.board.is_check()):
                window["Bewertung"].update("Schach")
                print("Schach")
            return True
        else:
            return False

    def make_move(self, move):
        self.board.push(move)

    def print_board(self):
        print(self.board)

def main():
    engine = Chessi_v07()

    layout = [
        [sg.Text("Schachengine", font=("Helvetica", 20))],
        [sg.Graph(canvas_size=(400, 400), graph_bottom_left=(0, 0), graph_top_right=(400, 400),
                  background_color='white', key='chess_board')],
        [sg.Button("Engine Zug", key="engine_move"), sg.Button("Neues Spiel", key="new_game")]
    ]

    window = sg.Window("Chessi Version 7", layout, finalize=True)
    board_graph = window['chess_board']
    # board_image = window["board_image"]
    # update_board_image(board_image, engine.board) # Das Brett anzeigen

    draw_chessboard(board_graph, engine.board)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == 'chess_board':
            if values['chess_board'] is not None:
                move_from = square_to_coordinates(values['chess_board'][0])
                move_to = square_to_coordinates(values['chess_board'][1])
                move = coordinates_to_move(move_from, move_to)
                if move is not None:
                    if engine.human_move(move_from, move_to, window):
                        engine.print_board()
                        draw_chessboard(board_graph, engine.board)
                    else:
                        sg.popup("Ungültiger Zug. Bitte versuche es erneut.")
        elif event == "engine_move":
            move = engine.get_move(window)
            engine.make_move(move)
            engine.print_board()
            draw_chessboard(board_graph, engine.board)
        elif event == "new_game":
            #engine.set_fen(chess.STARTING_FEN)
            draw_chessboard(board_graph, engine.board)

    window.close()

def draw_chessboard(board_graph, chess_board):
    board_graph.erase()
    colors = ['white', 'lightgray']
    for rank in range(8):
        for file in range(8):
            square = chess.square(file, rank)
            color = colors[(rank + file) % 2]
            board_graph.draw_rectangle((file * 50, (7 - rank) * 50), (file * 50 + 50, (7 - rank) * 50 + 50), fill_color=color)
            piece = chess_board.piece_at(square)
            if piece is not None:
                filename = get_piece_image(piece)
                board_graph.draw_image(filename, location=(file * 50, (7 - rank) * 50))

def update_board_image(board_image, chess_board):
    img = create_chessboard_image(chess_board)
    img_byte_array = BytesIO()
    img.save(img_byte_array, format="PNG")
    board_image.update(data=img_byte_array.getvalue())

def create_chessboard_image(chess_board):
    # Erstelle ein leeres PIL-Bild
    img = Image.new("RGB", (400, 400), color=(255, 255, 255))

    # Definiere die Farben für die Schachbrett-Felder
    light_square = (238, 238, 210)
    dark_square = (193,205,205)

    # Iteriere über das Schachbrett und fülle die Farben
    for row in range(8):
        for col in range(8):
            if (row + col) % 2 == 0:
                color = light_square
            else:
                color = dark_square
            x1, y1, x2, y2 = col * 50, row * 50, (col + 1) * 50, (row + 1) * 50
            img.paste(color, (x1, y1, x2, y2))

    # Füge die Schachfiguren hinzu
    for square in chess.SQUARES:
        piece = chess_board.piece_at(square)
        if piece is not None:
            piece_image = get_piece_image(piece)
            if piece_image is not None:
                x, y = get_image_position(square)
                img.paste(piece_image, (x, y), piece_image)

    return img

def get_piece_image(piece):
    piece_names = {
        "p": "pawnB.png",
        "r": "rookB.png",
        "n": "knightB.png",
        "b": "bishopB.png",
        "q": "queenB.png",
        "k": "kingB.png",
        "P": "pawnW.png",
        "R": "rookW.png",
        "N": "knightW.png",
        "B": "bishopW.png",
        "Q": "queenW.png",
        "K": "kingW.png"
    }
    if piece.symbol() in piece_names:
        return Image.open("/home/harald/Entwicklung/Python/Chessi/Figuren/" + piece_names[piece.symbol()])
    else:
        return None

def square_to_coordinates(square):
    file = chess.square_file(square)
    rank = chess.square_rank(square)
    return file * 50, (7 - rank) * 50

def coordinates_to_move(start, end):
    file_start = start[0] // 50
    rank_start = 7 - (start[1] // 50)
    file_end = end[0] // 50
    rank_end = 7 - (end[1] // 50)
    move = chess.Move(chess.square(file_start, rank_start), chess.square(file_end, rank_end))
    return move.uci() \
        # if move in engine.board.legal_moves else None

def get_image_position(square):
    file_names = "abcdefgh"
    file_idx = chess.square_file(square)
    rank_idx = 7 - chess.square_rank(square)
    x = file_idx * 50
    y = rank_idx * 50
    return x, y

if __name__ == "__main__":
    main()
