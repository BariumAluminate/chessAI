import pygame
import chess
from chess.svg import piece
from MoveGenerator import MoveGenerator

# Cấu hình kích thước
WIDTH, HEIGHT = 600, 600
CHESS_SIZE = WIDTH // 8
FPS = 30

# Màu sắc
WHITE = (240, 217, 181)
GREY = (181, 136, 99)
HIGHLIGHT = (130, 151, 105)
MOVE_HIGHLIGHT = (185, 201, 165)


class ChessGame:
    def __init__(self):
        self.board = chess.Board()
        self.move_gen = MoveGenerator(self.board)
        self.highlighted_squares = []
        self.selected_square = None
        self.game_over = False
        self.game_result = ""
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Gemini Chess AI Engine")

    def draw_board(self):
        """Vẽ các ô vuông trên bàn cờ"""
        for r in range(8):
            for c in range(8):
                square = chess.square(c, 7 - r)
                if square == self.selected_square:
                    color = HIGHLIGHT
                else:
                    color = WHITE if (r + c) % 2 == 0 else GREY

                pygame.draw.rect(
                    self.screen,
                    color,
                    pygame.Rect(c * CHESS_SIZE, r * CHESS_SIZE, CHESS_SIZE, CHESS_SIZE),
                )

    def draw_move_indicators(self):
        """Vẽ các chấm tròn chỉ những ô có thể di chuyển"""
        # Lặp qua từng ô trong self.highlighted_squares
        for square in self.highlighted_squares:
            # Tính r, c từ square
            row = 7 - (square // 8)
            col = square % 8

            # Tính tọa độ giữa ô
            center_x = col * CHESS_SIZE + CHESS_SIZE // 2
            center_y = row * CHESS_SIZE + CHESS_SIZE // 2

            # Vẽ chấm tròn
            pygame.draw.circle(
                self.screen,
                (50, 50, 50),
                (center_x, center_y),
                8
            )

    def draw_pieces(self):
        """Hiển thị quân cờ bằng ký tự Unicode"""
        font = pygame.font.Font("CASEFONT.TTF", 70)

        # Bảng ánh xạ quân cờ sang ký tự Unicode
        # lower case là quân đen
        # upper case là quân trắng
        unicode_pieces = {
            "P": "o",
            "N": "m",
            "B": "v",
            "R": "t",
            "Q": "w",
            "K": "l",
            "p": "o",
            "n": "m",
            "b": "v",
            "r": "t",
            "q": "w",
            "k": "l",
        }

        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                # Lấy ký hiệu (P, n, R,...) và tìm ký tự Unicode tương ứng
                piece_char = unicode_pieces.get(piece.symbol())

                # Màu sắc và border
                if piece.color == chess.WHITE:
                    color = (255, 255, 255)
                    border_color = (0, 0, 0)  # border đen cho quân trắng
                else:
                    color = (0, 0, 0)
                    border_color = (255, 255, 255)  # border trắng cho quân đen

                # Tính toán tọa độ để căn giữa ô chính xác
                col = square % 8
                row = 7 - (square // 8)
                center_x = col * CHESS_SIZE + CHESS_SIZE // 2
                center_y = row * CHESS_SIZE + CHESS_SIZE // 2

                # Vẽ border bằng cách vẽ text ở các vị trí xung quanh
                border_offset = 2
                for dx in [-border_offset, 0, border_offset]:
                    for dy in [-border_offset, 0, border_offset]:
                        if dx != 0 or dy != 0:
                            border_surface = font.render(piece_char, True, border_color)
                            border_rect = border_surface.get_rect(
                                center=(center_x + dx, center_y + dy)
                            )
                            self.screen.blit(border_surface, border_rect)

                # Vẽ quân cờ chính trên border
                text_surface = font.render(piece_char, True, color)
                text_rect = text_surface.get_rect(center=(center_x, center_y))
                self.screen.blit(text_surface, text_rect)

    def draw_game_status(self):
        """Vẽ thông báo game over"""
        if self.game_over:
            font_large = pygame.font.Font(None, 50)
            font_small = pygame.font.Font(None, 40)
            
            # Thông báo chiếu hết (trên)
            text_result = font_large.render(self.game_result, True, (255, 255, 0))
            rect_result = text_result.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
            
            # Vẽ nền đen cho thông báo chiếu hết
            bg_rect_result = rect_result.inflate(40, 20)
            pygame.draw.rect(self.screen, (0, 0, 0), bg_rect_result)
            pygame.draw.rect(self.screen, (200, 200, 0), bg_rect_result, 3)  # Border vàng
            self.screen.blit(text_result, rect_result)
            
            # Thông báo "Press R to Play Again" (dưới)
            text_restart = font_small.render("Press R to Play Again", True, (255, 255, 0))
            rect_restart = text_restart.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
            
            # Vẽ nền đen cho thông báo Play Again
            bg_rect_restart = rect_restart.inflate(40, 20)
            pygame.draw.rect(self.screen, (0, 0, 0), bg_rect_restart)
            pygame.draw.rect(self.screen, (200, 200, 0), bg_rect_restart, 3)  # Border vàng
            self.screen.blit(text_restart, rect_restart)

    def check_game_status(self):
        """Kiểm tra game kết thúc chưa"""
        if self.move_gen.isCheckmate():
            self.game_over = True
            # Nguời chơi trước khi checkmate là người thắng
            if self.board.turn == chess.WHITE:  # Đen vừa checkmate
                self.game_result = "Black wins by checkmate!"
            else:
                self.game_result = "White wins by checkmate!"
                
        elif self.move_gen.isStalemate():
            self.game_over = True
            self.game_result = "Draw - Stalemate!"
            
        elif self.board.is_insufficient_material():
            self.game_over = True
            self.game_result = "Draw - Insufficient material!"

    def get_square_under_mouse(self):
        mouse_pos = pygame.mouse.get_pos()
        col = mouse_pos[0] // CHESS_SIZE
        row = 7 - (mouse_pos[1] // CHESS_SIZE)
        return chess.square(col, row)

    def run(self):
        clock = pygame.time.Clock()
        running = True  # test
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    square = self.get_square_under_mouse()

                    if self.selected_square is None:
                        # Chọn quân cờ
                        if self.board.piece_at(square):
                            self.selected_square = square

                            # Lấy moves
                            self.highlighted_squares = [move.to_square for move in self.move_gen.getLegalMoves(self.selected_square)]

                    elif square == self.selected_square:
                        self.selected_square = None
                        self.highlighted_squares = []

                    else:
                        # Thực hiện nước đi
                        move = chess.Move(self.selected_square, square)

                        # Kiểm tra phong cấp (mặc định lên Hậu)
                        if (
                            self.move_gen.isMoveLegal(self.selected_square, square)
                            or chess.Move(self.selected_square, square, chess.QUEEN)
                            in self.board.legal_moves
                        ):
                            if (
                                chess.Move(self.selected_square, square, chess.QUEEN)
                                in self.board.legal_moves
                            ):
                                move = chess.Move(
                                    self.selected_square, square, chess.QUEEN
                                )

                            self.board.push(move)
                            self.selected_square = None
                            self.highlighted_squares = []
                            self.check_game_status()

                        #Di chuyển không hợp lệ
                        else:
                            piece_at_square = self.board.piece_at(square)
                            if piece_at_square and piece_at_square.color == self.board.turn:
                                self.selected_square = square
                                self.highlighted_squares = [move.to_square for move in self.move_gen.getLegalMoves(self.selected_square)]
                            else: 
                                self.selected_square = None
                                self.highlighted_squares = []

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and self.game_over:
                        #Reset Game
                        self.board = chess.Board()
                        self.move_gen = MoveGenerator(self.board)
                        self.selected_square = None
                        self.highlighted_squares = []
                        self.game_over = False
                        self.game_result = ""

            self.screen.fill((0, 0, 0))
            self.draw_board()
            self.draw_pieces()
            self.draw_move_indicators()
            self.draw_game_status()
            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()


if __name__ == "__main__":
    pygame.init()
    game = ChessGame()
    game.run()
