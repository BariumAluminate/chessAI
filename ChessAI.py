import chess
import pygame
from chess.svg import piece

def evaluate_board(board):
    """Hàm tự viết để AI chấm điểm: Dương là Trắng ưu thế, Âm là Đen ưu thế"""
    if board.is_checkmate():
        # Nếu Trắng bị chiếu hết thì Đen thắng (điểm cực âm) và ngược lại
        return -99999 if board.turn == chess.WHITE else 99999
    if board.is_game_over():
        return 0  # Hòa cờ

    # Bảng giá trị quân cờ
    piece_values = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 20000
    }

    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            val = piece_values[piece.piece_type]
            # Cộng điểm cho Trắng, trừ điểm cho Đen
            if piece.color == chess.WHITE:
                score += val
            else:
                score -= val
    return score

class ChessAI:
    def __init__(self, board):
        self.board = board
        self.max_depth = 3
        # Bảng điểm quân cờ
        self.PIECE_VALUES = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 0
        }


    def evaluate_board(self):
        """
        Hàm đánh giá: Trả về (Điểm trắng - Điểm đen).
        Số dương: Trắng ưu thế. Số âm: Đen ưu thế.
        """
        if self.board.is_checkmate():
            if self.board.turn == chess.WHITE:
                return -99999 #Đen thắng
            else:
                return 99999 #Trắng thắng
            
        score = 0
        #Lặp qua tất cả các ô trên bàn cờ
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                val = self.PIECE_VALUES.get(piece.piece_type, 0)
                if piece.color == chess.WHITE:
                    score += val
                else:
                    score -= val
        return score
    

    # ==========================
    # THUẬT TOÁN MINIMAX
    # ==========================
    def minimax(self, depth, is_maximizing):
        """
        Thuật toán Minimax đệ quy
        depth: độ sâu còn lại cần tính
        is_maximizing: True nếu là lượt của Trắng, False nếu là Đen
        """
        # Điều kiện dừng: đạt độ sâu tối đa hoặc game kết thúc
        if depth == 0 or self.board.is_game_over():
            return self.evaluate_board()
        
        if is_maximizing:
            max_evaluate = -float('inf')
            for move in self.board.legal_moves:
                self.board.push(move)
                evaluate = self.minimax(depth - 1, False) #Đệ quy và đổi lượt
                self.board.pop()
                max_evaluate = max(max_evaluate, evaluate)
            return max_evaluate
        else:
            min_evaluate = float('inf')
            for move in self.board.legal_moves:
                self.board.push(move)
                evaluate = self.minimax(depth - 1, True) #Đệ quy và đổi lượt
                self.board.pop()
                min_evaluate = min(min_evaluate, evaluate)
            return min_evaluate
        

    def get_minimax_move(self, depth=3):
        """Để mặc định độ sâu là 3"""
        best_move = None

        if self.board.turn == chess.WHITE:
            best_value = -float('inf')
            for move in self.board.legal_moves:
                self.board.push(move)
                value = self.minimax(depth, False)
                self.board.pop()
                
                if value > best_value:
                    best_value = value
                    best_move = move
        
        else:
            best_value = float('inf')
            for move in self.board.legal_moves:
                self.board.push(move)
                value = self.minimax(depth, True)
                self.board.pop()

                if value < best_value:
                    best_value = value
                    best_move = move
        
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
