import chess
import pygame
from chess.svg import piece

import chess

# Định nghĩa giá trị cơ bản của các quân cờ
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

PAWN_PST = [
    0, 0, 0, 0, 0, 0, 0, 0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
    5, 5, 10, 25, 25, 10, 5, 5,
    0, 0, 0, 20, 20, 0, 0, 0,
    5, -5, -10, 0, 0, -10, -5, 5,
    5, 10, 10, -20, -20, 10, 10, 5,
    0, 0, 0, 0, 0, 0, 0, 0
][::-1]

KNIGHT_PST = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20, 0, 0, 0, 0, -20, -40,
    -30, 0, 10, 15, 15, 10, 0, -30,
    -30, 5, 15, 20, 20, 15, 5, -30,
    -30, 0, 15, 20, 20, 15, 0, -30,
    -30, 5, 10, 15, 15, 10, 5, -30,
    -40, -20, 0, 5, 5, 0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50
][::-1]


def evaluate_board(board: chess.Board) -> int:
    """
    Hàm đánh giá thế trận hiện tại của bàn cờ.
    Trả về điểm số: Dương (Trắng lợi), Âm (Đen lợi).
    """
    # Kiểm tra trạng thái kết thúc game trước
    if board.is_checkmate():
        # Nếu đang đến lượt Trắng mà bị chiếu hết -> Đen thắng (-vô cùng)
        return -99999 if board.turn == chess.WHITE else 99999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    score = 0

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is None:
            continue

        value = PIECE_VALUES[piece.piece_type]

        pst_bonus = 0

        eval_square = square if piece.color == chess.WHITE else chess.square_mirror(square)

        if piece.piece_type == chess.PAWN:
            pst_bonus = PAWN_PST[eval_square]
        elif piece.piece_type == chess.KNIGHT:
            pst_bonus = KNIGHT_PST[eval_square]

        total_piece_score = value + pst_bonus

        if piece.color == chess.WHITE:
            score -= total_piece_score
        else:
            score += total_piece_score

    return score

class ChessAI:
    def __init__(self, board):
        self.board = board
        self.max_depth = 4
        # Bảng điểm quân cờ
        self.PIECE_VALUES = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 0
        }

    # ======================================
    # HÀM ĐÁNH GIÁ
    # ======================================
    def evaluate_board(self):
        """
        Hàm đánh giá: Trả về (Điểm trắng - Điểm đen).
        Số dương: Trắng ưu thế. Số âm: Đen ưu thế.
        """
        if self.board.is_checkmate():
            if self.board.turn == chess.WHITE:
                return -99999
            else:
                return 99999

        if self.board.is_stalemate():
            return 0

        score = 0

        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                val = self.PIECE_VALUES.get(piece.piece_type, 0)
                if piece.color == chess.WHITE:
                    score += val
                else:
                    score -= val
        return score

    # ======================================
    # SẮP XẾP NƯỚC ĐI
    # ======================================
    def order_moves(self, moves):
        """
        Sắp xếp nước đi:
        - ưu tiên ăn quân giá trị cao
        - ưu tiên chiếu vua
        """

        def move_score(move):

            score = 0

            """Nếu là nước ăn quân"""
            if self.board.is_capture(move):

                captured_piece = self.board.piece_at(move.to_square)
                moving_piece = self.board.piece_at(move.from_square)

                if captured_piece and moving_piece:
                    score += (
                            10 * self.PIECE_VALUES[captured_piece.piece_type]
                            - self.PIECE_VALUES[moving_piece.piece_type]
                            #Ưu tiên dùng con nhỏ ăn con to
                    )

            """Nếu là nước chiếu"""
            self.board.push(move)

            if self.board.is_check():
                score += 50

            self.board.pop()

            return score

        return sorted(moves, key=move_score, reverse=True)



    # ==========================
    # THUẬT TOÁN MINIMAX + cắt tỉa Alpha Beta
    # ==========================
    def minimax(self, depth, alpha, beta):
        """
        Thuật toán Minimax đệ quy
        depth: độ sâu còn lại cần tính
        is_maximizing: True nếu là lượt của Trắng, False nếu là Đen
        """
        # Điều kiện dừng: đạt độ sâu tối đa hoặc game kết thúc
        if depth == 0 or self.board.is_game_over():
            return self.evaluate_board()

        moves = self.order_moves(list(self.board.legal_moves))

        # ==================================
        # WHITE -> MAX
        # ==================================
        if self.board.turn == chess.WHITE:

            max_eval = -float('inf')

            for move in moves:

                self.board.push(move)

                evaluation = self.minimax(
                    depth - 1,
                    alpha,
                    beta
                )

                self.board.pop()

                max_eval = max(max_eval, evaluation)

                alpha = max(alpha, evaluation)

                # Cắt tỉa Alpha-Beta
                if beta <= alpha:
                    break

            return max_eval
            # ==================================
            # BLACK -> MIN
            # ==================================
        else:

            min_eval = float('inf')

            for move in moves:

                self.board.push(move)

                evaluation = self.minimax(
                    depth - 1,
                    alpha,
                    beta
                )

                self.board.pop()

                min_eval = min(min_eval, evaluation)

                beta = min(beta, evaluation)

                # Cắt tỉa Alpha-Beta
                if beta <= alpha:
                    break

            return min_eval
        

    def get_minimax_move(self, depth=3):
        """Để mặc định độ sâu là 3"""
        best_move = None

        moves = self.order_moves(list(self.board.legal_moves))

        if self.board.turn == chess.WHITE:
            best_value = -float('inf')
            alpha = -float('inf')  # Khởi tạo alpha ở gốc
            beta = float('inf')

            for move in moves:
                self.board.push(move)
                value = self.minimax(
                    depth - 1,
                    alpha,
                    beta
                )
                self.board.pop()
                
                if value > best_value:
                    best_value = value
                    best_move = move

                alpha = max(alpha, best_value) # cập nhật alpha
        
        else:
            best_value = float('inf')
            alpha = -float('inf')
            beta = float('inf')  # Khởi tạo beta ở gốc

            for move in self.board.legal_moves:
                self.board.push(move)
                value = self.minimax(
                    depth - 1,
                    alpha,
                    beta
                )
                self.board.pop()

                if value < best_value:
                    best_value = value
                    best_move = move

                beta = min(beta, best_value) # cập nhật beta
        
        return best_move

    def negamax(self):
        best_value = -float('inf')
        alpha = -float('inf')
        beta = float('inf')
        # Lấy ngay phần tử đầu tiên mà không cần chuyển đổi cả danh sách
        best_move = next(iter(self.board.legal_moves))
        for move in self.board.legal_moves:
            self.board.push(move)
            a = self.ngm(alpha, beta, 1)
            if best_value < a:
                best_value = a
                best_move = move
            if best_value > beta:
                return best_move
            alpha = max(alpha, best_value)
            self.board.pop()
        return best_move

    def ngm(self, alpha, beta, depth: int):
        # 1. Điều kiện dừng: CHỈ đánh giá thế cờ hiện tại, TUYỆT ĐỐI KHÔNG pop ở đây
        if depth == self.max_depth or self.board.is_game_over():
            return evaluate_board(self.board)

        # Nhánh MAX (Lượt chẵn)
        if depth % 2 == 0:
            best_value = -float('inf')
            for move in self.board.legal_moves:
                self.board.push(move)
                best_value = max(best_value, self.ngm(alpha, beta, depth + 1))
                self.board.pop()  # Pop ngay sau khi nhánh đệ quy kết thúc

                alpha = max(alpha, best_value)
                if best_value >= beta:
                    break  # Dùng break thay vì return để không bị nuốt mất lệnh pop() phía trên
            return best_value

        # Nhánh MIN (Lượt lẻ)
        else:
            best_value = float('inf')
            for move in self.board.legal_moves:
                self.board.push(move)
                best_value = min(best_value, self.ngm(alpha, beta, depth + 1))
                self.board.pop()  # Pop ngay sau khi nhánh đệ quy kết thúc

                beta = min(beta, best_value)
                if best_value <= alpha:
                    break  # Dùng break để thoát vòng lặp an toàn
            return best_value





    # ==========================
    # THUẬT TOÁN THAM LAM (GREEDY)
    # ==========================
    def get_best_move(self):
        """Tìm nước đi tốt nhất theo cách tham lam(chỉ nhìn trước được 1 bước)"""
        best_move = None

        # Nếu là lượt Trắng -> tìm score cao nhất (max)
        # Nếu là lượt Đen -> tìm score thấp nhất (min)
        if self.board.turn == chess.WHITE:
            max_score = -float('inf')
            for move in self.board.legal_moves:
                self.board.push(move)
                score = self.evaluate_board()
                self.board.pop()

                if score > max_score:
                    max_score = score
                    best_move = move
        
        else:
            min_score = float('inf')
            for move in self.board.legal_moves:
                self.board.push(move)
                score = self.evaluate_board()
                self.board.pop()

                if score < min_score:
                    min_score = score
                    best_move = move
        
        return best_move
