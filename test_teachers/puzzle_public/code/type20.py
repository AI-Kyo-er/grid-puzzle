import json
import ast

# 示例输入数据（需替换为实际JSON文件读取）



def type_prompts(item):
    init_str = item["initialization"]
    init_dict = ast.literal_eval(init_str)
    file_name = item["file_name"]
    text = ""
    # Aquarium
    if "aquarium" in file_name:
        inner_init = init_dict["initialization"]
        clues = inner_init["clues"]
        board = inner_init["board"]
        row_counts = clues["row_counts"]
        col_counts = clues["col_counts"]
        aquariums = clues["aquariums"]
        text = f"This is an Aquarium puzzle, a grid-based puzzle where you need to fill cells with water based on given clues.\nVisual information:\n- Grid size: {init_dict['size']}x{init_dict['size']}\n- Initial board: {board}\n- Row clues: {row_counts}\n- Column clues: {col_counts}\n- Aquarium regions: {aquariums}"
    # Battleships
    elif "battleships" in file_name:
        size = init_dict["size"]
        hints = init_dict["hints"]
        row_hints = hints["row_hints"]
        col_hints = hints["col_hints"]
        ships = hints["ships"]
        ship_direction_map = hints["ship_direction_map"]
        board = init_dict["initialization"]
        text = f"This is a Battleships puzzle, where you need to place ships on a grid according to given clues.\nVisual information:\n- Grid size: {size}x{size}\n- Initial board: {board}\n- Row hints: {row_hints}\n- Column hints: {col_hints}\n- Number of ships: {ships}\n- Ship directions: {ship_direction_map}"
    # Binairo
    elif "binairo" in file_name:
        board = init_dict["initialization"]
        text = f"This is a Binairo puzzle, a binary puzzle where you need to fill the grid with 0s and 1s following specific rules.\nVisual information:\n- Initial board: {board}"
    # Colored Sudoku
    elif "coloredsudoku" in file_name:
        board = init_dict["initialization"]
        colors = init_dict["colors"]
        text = f"This is a Colored Sudoku puzzle, a variant of Sudoku where cells are colored and must follow additional color-based rules.\nVisual information:\n- Grid size: {init_dict['size']}x{init_dict['size']}\n- Initial board: {board}\n- Color regions: {colors}"
    # Minesweeper
    elif "fieldexplore" in file_name:
        board = init_dict["initialization"]
        text = f"This is a Minesweeper puzzle, where you need to identify the locations of mines based on number clues.\nVisual information:\n- Grid size: {init_dict['size']}x{init_dict['size']}\n- Initial board: {board}"
    # Futoshiki
    elif "futoshiki" in file_name:
        board = init_dict["initialization"]
        row_ineq = init_dict["row_inequalities"]
        col_ineq = init_dict["col_inequalities"]
        text = f"This is a Futoshiki puzzle, a grid puzzle with inequality constraints between adjacent cells.\nVisual information:\n- Grid size: {init_dict['size']}x{init_dict['size']}\n- Initial board: {board}\n- Row inequalities: {row_ineq}\n- Column inequalities: {col_ineq}"
    # Hitori
    elif "hitori" in file_name:
        board = init_dict["initialization"]["board"]
        numbers = init_dict["initialization"]["numbers"]
        text = f"This is a Hitori puzzle, where you need to black out cells to create a valid solution.\nVisual information:\n- Grid size: {init_dict['size']}x{init_dict['size']}\n- Initial board: {board}\n- Number distribution: {numbers}"
    # Jigsaw Sudoku
    elif "jigsawsudoku" in file_name:
        board = init_dict["initialization"]
        regions = init_dict["regions"]
        text = f"This is a Jigsaw Sudoku puzzle, a variant of Sudoku with irregular regions.\nVisual information:\n- Grid size: {init_dict['size']}x{init_dict['size']}\n- Initial board: {board}\n- Regions: {regions}"
    # Kakurasu
    elif "kakurasu" in file_name:
        board = init_dict["initialization"]["board"]
        row_clues = init_dict["initialization"]["clues"]["row_clues"]
        col_clues = init_dict["initialization"]["clues"]["col_clues"]
        text = f"This is a Kakurasu puzzle, where you need to shade cells to match given row and column sums.\nVisual information:\n- Grid size: {init_dict['size']}x{init_dict['size']}\n- Initial board: {board}\n- Row clues: {row_clues}\n- Column clues: {col_clues}"
    # Kakuro
    elif "kakuro" in file_name:
        board = init_dict["initialization"]
        sums = init_dict["sums"]
        row_sum = sums["row"]
        col_sum = sums["col"]
        text = f"This is a Kakuro puzzle, a cross-sum puzzle where you need to fill cells with numbers that sum to given values.\nVisual information:\n- Grid size: {init_dict['size']}x{init_dict['size']}\n- Initial board: {board}\n- Row sums: {row_sum}\n- Column sums: {col_sum}"
    # Killer Sudoku
    elif "killersudoku" in file_name:
        board = init_dict["initialization"]
        cages = init_dict["cages"]
        text = f"This is a Killer Sudoku puzzle, a variant of Sudoku with additional cage constraints.\nVisual information:\n- Grid size: {init_dict['size']}x{init_dict['size']}\n- Initial board: {board}\n- Cage information: {cages}"
    # Light Up
    elif "lightup" in file_name:
        board = init_dict["initialization"]
        wall_numbers = init_dict["wall_numbers"]
        text = f"This is a Light Up puzzle, where you need to place light bulbs to illuminate the entire grid.\nVisual information:\n- Grid size: {init_dict['size']}x{init_dict['size']}\n- Initial board: {board}\n- Wall numbers: {wall_numbers}"
    # Nonogram
    elif "nonogram" in file_name:
        board = init_dict["initialization"]
        hints = init_dict["hints"]
        row_hints = hints["row_hints"]
        col_hints = hints["col_hints"]
        text = f"This is a Nonogram puzzle, where you need to reveal a hidden picture by following number clues.\nVisual information:\n- Grid size: {init_dict['size']}x{init_dict['size']}\n- Initial board: {board}\n- Row hints: {row_hints}\n- Column hints: {col_hints}"
    # Odd-Even Sudoku
    elif "oddevensudoku" in file_name:
        board = init_dict["initialization"]
        cell_types = init_dict["cell_types"]
        text = f"This is an Odd-Even Sudoku puzzle, where cells are marked as odd or even.\nVisual information:\n- Grid size: {init_dict['size']}x{init_dict['size']}\n- Initial board: {board}\n- Cell types: {cell_types}"
    # Renzoku
    elif "renzoku" in file_name:
        board = init_dict["initialization"]
        hints = init_dict["hints"]
        text = f"This is a Renzoku puzzle, a number placement puzzle with specific rules.\nVisual information:\n- Grid size: {init_dict['size']}x{init_dict['size']}\n- Initial board: {board}\n- Hints: {hints}"
    # Skyscraper
    elif "skyscraper" in file_name:
        board = init_dict["initialization"]["board"]
        clues = init_dict["initialization"]["clues"]
        text = f"This is a Skyscraper puzzle, where you need to place buildings of different heights.\nVisual information:\n- Grid size: {init_dict['size']}x{init_dict['size']}\n- Initial board: {board}\n- Clues: {clues}"
    # Star Battle
    elif "starbattle" in file_name:
        board = init_dict["initialization"]
        regions = init_dict["regions"]
        num_stars = init_dict["num_stars"]
        text = f"This is a Star Battle puzzle, where you need to place stars in regions according to rules.\nVisual information:\n- Grid size: {init_dict['size']}x{init_dict['size']}\n- Initial board: {board}\n- Regions: {regions}\n- Number of stars: {num_stars}"
    # Standard Sudoku
    elif "sudoku" in file_name and "jigsawsudoku" not in file_name and "killersudoku" not in file_name and "coloredsudoku" not in file_name and "oddevensudoku" not in file_name:
        board = init_dict["initialization"]
        text = f"This is a standard Sudoku puzzle, where you need to fill a 9x9 grid with numbers 1-9.\nVisual information:\n- Grid size: {init_dict['size']}x{init_dict['size']}\n- Initial board: {board}"
    # Thermometers
    elif "thermometers" in file_name:
        board = init_dict["initialization"]["board"]
        clues = init_dict["initialization"]["clues"]
        row_counts = clues["row_counts"]
        col_counts = clues["col_counts"]
        thermometers = clues["thermometers"]
        text = f"This is a Thermometers puzzle, where you need to fill thermometers with mercury.\nVisual information:\n- Grid size: {init_dict['size']}x{init_dict['size']}\n- Initial board: {board}\n- Row counts: {row_counts}\n- Column counts: {col_counts}\n- Thermometer positions: {thermometers}"
    # Trees and Tents
    elif "treesandtents" in file_name:
        board = init_dict["initialization"]
        clues = init_dict["clues"]
        row_clues = clues["row_clues"]
        col_clues = clues["col_clues"]
        text = f"This is a Trees and Tents puzzle, where you need to place tents next to trees.\nVisual information:\n- Grid size: {init_dict['size']}x{init_dict['size']}\n- Initial board: {board}\n- Row clues: {row_clues}\n- Column clues: {col_clues}"
    return text
