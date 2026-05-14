import pygame
import chess
from chess.svg import piece

# Cấu hình kích thước
WIDTH, HEIGHT = 600, 600
CHESS_SIZE = WIDTH // 8
FPS = 30

# Màu sắc
WHITE = (240, 217, 181)
GREY = (181, 136, 99)
HIGHLIGHT = (130, 151, 105)


class ChessGame:
    def __init__(self):
        self.board = chess.Board()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Gemini Chess AI Engine")
        self.selected_square = None

    def draw_board(self):
        """Vẽ các ô vuông trên bàn cờ"""
        for r in range(8):
            for c in range(8):
                color = WHITE if (r + c) % 2 == 0 else GREY
                if self.selected_square is not None:
                    if r == 7 - (self.selected_square // 8) and c == self.selected_square % 8:
                        color = HIGHLIGHT
                pygame.draw.rect(self.screen, color,
                                 pygame.Rect(c * CHESS_SIZE, r * CHESS_SIZE, CHESS_SIZE, CHESS_SIZE))

    def draw_pieces(self):
        """Hiển thị quân cờ bằng ký tự Unicode"""
        # Sử dụng font hỗ trợ tốt các ký tự đặc biệt
        font = pygame.font.SysFont("FreeSerif", 60)

        # Bảng ánh xạ quân cờ sang ký tự Unicode
        unicode_pieces = {
            'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟',
            'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙'
        }

        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                # Lấy ký hiệu (P, n, R,...) và tìm ký tự Unicode tương ứng
                piece_char = unicode_pieces.get(piece.symbol())

                # Màu sắc (thường các ký tự Unicode đã có hình dạng đen/trắng rõ ràng)
                # Bạn có thể để màu đen hoàn toàn cho cả hai để tận dụng hình vẽ của font
                color = (0, 0, 0)

                text_surface = font.render(piece_char, True, color)

                # Tính toán tọa độ để căn giữa ô
                col = square % 8
                row = 7 - (square // 8)

                # Căn chỉnh một chút (+10, +5) để quân cờ nằm giữa ô
                pos = (col * CHESS_SIZE + 15, row * CHESS_SIZE + 5)
                self.screen.blit(text_surface, pos)

    def get_square_under_mouse(self):
        mouse_pos = pygame.mouse.get_pos()
        col = mouse_pos[0] // CHESS_SIZE
        row = 7 - (mouse_pos[1] // CHESS_SIZE)
        return chess.square(col, row)

    def run(self):
        clock = pygame.time.Clock()
        running = True#test
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
                    else:
                        # Thực hiện nước đi
                        move = chess.Move(self.selected_square, square)

                        # Kiểm tra phong cấp (mặc định lên Hậu)
                        if move in self.board.legal_moves or chess.Move(self.selected_square, square,
                                                                        chess.QUEEN) in self.board.legal_moves:
                            if chess.Move(self.selected_square, square, chess.QUEEN) in self.board.legal_moves:
                                move = chess.Move(self.selected_square, square, chess.QUEEN)
                            self.board.push(move)

                        self.selected_square = None

            self.screen.fill((0, 0, 0))
            self.draw_board()
            self.draw_pieces()
            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()


if __name__ == "__main__":
    pygame.init()
    game = ChessGame()
    game.run()