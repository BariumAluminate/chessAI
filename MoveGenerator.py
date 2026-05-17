import chess


class MoveGenerator:
    """Class quản lý tất cả logic liên quan tới nước đi cờ"""
    
    # ===== ĐIỂM SỐ CỦA TỪNG LOẠI QUÂN =====
    PIECE_VALUES = {
        chess.PAWN: 100,
        chess.KNIGHT: 300,
        chess.BISHOP: 300,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 0,
    }

    def __init__(self, board):
        """Khởi tạo MoveGenerator với board từ bên ngoài
        
        Args:
            board: chess.Board object (bàn cờ hiện tại)
        """
        self.board = board

    # ===== MAIN FUNCTIONS =====
    
    def getState(self):
        """Lấy TẤT CẢ legal moves hiện tại
        
        Returns:
            list[chess.Move]: danh sách tất cả nước đi hợp lệ
        
        Ví dụ:
            moves = mg.getState()  # Có ~20 moves lúc đầu
            print(len(moves))      # 20
        """
        return list(self.board.legal_moves)

    def getLegalMoves(self, from_square):
        """Lấy legal moves của 1 quân cờ cụ thể
        
        Args:
            from_square: int (0-63), vị trí quân cờ
        
        Returns:
            list[chess.Move]: moves từ quân đó
        
        Ví dụ:
            moves = mg.getLegalMoves(chess.E2)  # Moves từ e2
            # Trả về: [e2e3, e2e4] (2 moves)
        """
        return [
            move for move in self.board.legal_moves 
            if move.from_square == from_square
        ]

    def isMoveLegal(self, from_square, to_square):
        """Kiểm tra 1 move có hợp lệ không
        
        Args:
            from_square: int (0-63), ô xuất phát
            to_square: int (0-63), ô đích
        
        Returns:
            bool: True nếu hợp lệ, False nếu không
        
        Ví dụ:
            valid = mg.isMoveLegal(chess.E2, chess.E4)  # True
        """
        for move in self.board.legal_moves:
            if move.from_square == from_square and move.to_square == to_square:
                return True
        return False

    # ===== PIECE INFO =====
    
    def getPieceAt(self, square):
        """Lấy quân cờ tại 1 ô cụ thể
        
        Args:
            square: int (0-63), vị trí ô
        
        Returns:
            chess.Piece or None: quân cờ tại ô (None nếu trống)
        
        Ví dụ:
            piece = mg.getPieceAt(chess.E2)
            if piece:
                print(piece.symbol())   # 'P' (Pawn trắng)
                print(piece.color)      # WHITE
        """
        return self.board.piece_at(square)

    def getValueAt(self, square):
        """Lấy điểm số (giá trị) của quân cờ tại ô
        
        Giải thích:
            - Pawn = 100 điểm
            - Knight/Bishop = 300 điểm
            - Rook = 500 điểm
            - Queen = 900 điểm
            - King = 0 (không thể tính giá trị)
        
        Args:
            square: int (0-63), vị trí ô
        
        Returns:
            int: điểm số của quân, 0 nếu ô trống
        
        Ví dụ:
            value = mg.getValueAt(chess.E2)    # 100 (Pawn)
            value = mg.getValueAt(chess.D1)    # 900(Queen)
            value = mg.getValueAt(chess.E4)    # 0 (ô trống)
        """
        piece = self.board.piece_at(square)
        if piece is None:
            return 0
        return self.PIECE_VALUES.get(piece.piece_type, 0)

    # ===== ATTACK INFO =====
    
    def getAttackedSquares(self, by_color):
        """Lấy TẤT CẢ ô bị tấn công bởi lực lượng hiện tại
        
        Giải thích:
            - Tìm tất cả nước đi có thể
            - Lấy ô đích của mỗi move
            - Những ô này là ô bị tấn công
        
        Returns:
            set: tập hợp các ô (square) bị tấn công
        
        Ví dụ:
            attacked = mg.getAttackedSquares()
            print(len(attacked))  # Số ô bị tấn công
        """
        attacked_squares = set()
        for square in chess.SQUARES:
            if self.board.is_attacked_by(by_color, square):
                attacked_squares.add(square)
        return attacked_squares

    def isSquareAttacked(self, square, by_color):
        """Kiểm tra 1 ô có bị tấn công không
        
        Args:
            square: int (0-63), ô cần check
        
        Returns:
            bool: True nếu bị tấn công, False nếu không
        
        Ví dụ:
            attacked = mg.isSquareAttacked(chess.E4)
            if attacked:
                print("Ô e4 bị tấn công!")
        """
        return self.board.is_attacked_by(by_color, square)

    # ===== GAME STATE =====
    
    def isCheck(self):
        """Kiểm tra bên hiện tại có đang bị chiếu không
        
        Returns:
            bool: True nếu đang bị chiếu
        
        Ví dụ:
            if mg.isCheck():
                print("Vua bị chiếu!")
        """
        return self.board.is_check()

    def isCheckmate(self):
        """Kiểm tra có phải Checkmate không
        
        Giải thích:
            - Bị chiếu AND
            - Không có nước đi hợp lệ nào
        
        Returns:
            bool: True nếu checkmate
        """
        return self.board.is_checkmate()

    def isStalemate(self):
        """Kiểm tra có phải Stalemate không (hòa)
        
        Giải thích:
            - KHÔNG bị chiếu AND
            - Không có nước đi hợp lệ nào
        
        Returns:
            bool: True nếu stalemate
        """
        return self.board.is_stalemate()

    def isGameOver(self):
        """Kiểm tra game kết thúc chưa
        
        Giải thích:
            - Checkmate OR Stalemate 
            - Không đủ quân để chiếu (vd: chỉ có vua) 
            - Repetition (lặp 3 lần) 
            - 50-move rule (50 nước không ăn/pion)
        
        Returns:
            bool: True nếu game kết thúc
        """
        return self.board.is_game_over()

    # ===== STATS =====
    
    def getMoveCount(self):
        """Lấy số lượng legal moves hiện tại
        
        Returns:
            int: số lượng nước đi có thể
        
        Ví dụ:
            count = mg.getMoveCount()
            print(f"Có {count} nước đi")
        """
        return self.board.legal_moves.count()

    def getGamePly(self):
        """Lấy tổng số nước đi đã chơi (half-moves)
        
        Giải thích:
            - Ply = half-move (nước đi của 1 bên)
            - Nếu chơi 10 nước mỗi bên = 20 ply
        
        Returns:
            int: số ply đã chơi
        
        Ví dụ:
            ply = mg.getGamePly()  # 0 lúc đầu
            # Sau khi e2e4 e7e5: ply = 2
        """
        return self.board.ply()
