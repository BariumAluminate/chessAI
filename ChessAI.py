import chess
import pygame
from chess.svg import piece

class ChessAI:
    def __init__(self, board):
        self.board = board
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
