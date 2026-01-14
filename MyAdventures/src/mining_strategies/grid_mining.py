"""Estratègia de mineria en quadrícula."""
import time
from .mining_strategy import MiningStrategy
from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from ..agents.miner import MinerAgent


class GridMining(MiningStrategy):
    """Mina una regió cúbica (10x10x5) per sota de la posició inicial."""

    # Mapatge de fallback per blocs que no estan a les constants de mcpi.block
    BLOCK_ID_NAMES = {
        0: "air",
        1: "stone",
        2: "grass",
        3: "dirt",
        4: "cobblestone",
        5: "oak_wood",
        6: "oak_leaves",
        7: "bedrock",
        8: "water",
        9: "water",
        10: "lava",
        11: "lava",
        12: "sand",
        13: "gravel",
        14: "gold_ore",
        15: "iron_ore",
        16: "coal_ore",
        17: "oak_log",
        18: "oak_leaves",
        19: "sponge",
        20: "glass",
        21: "lapis_ore",
        22: "lapis_block",
        24: "sandstone",
        25: "note_block",
        26: "bed",
        27: "powered_rail",
        28: "detector_rail",
        29: "sticky_piston",
        30: "cobweb",
        31: "tall_grass",
        32: "dead_bush",
        33: "piston",
        34: "piston_head",
        35: "wool",
        36: "moving_block",
        37: "dandelion",
        38: "poppy",
        39: "brown_mushroom",
        40: "red_mushroom",
        41: "gold_block",
        42: "iron_block",
        43: "double_slab",
        44: "slab",
        45: "brick",
        46: "tnt",
        47: "bookshelf",
        48: "mossy_cobblestone",
        49: "obsidian",
        50: "torch",
        51: "fire",
        52: "mob_spawner",
        53: "oak_stairs",
        54: "chest",
        55: "redstone_wire",
        56: "diamond_ore",
        57: "diamond_block",
        58: "crafting_table",
        59: "wheat",
        60: "farmland",
        61: "furnace",
        62: "lit_furnace",
        63: "standing_sign_block",
        64: "oak_door",
        65: "ladder",
        66: "rail",
        67: "stone_stairs",
        68: "wall_sign",
        69: "lever",
        70: "stone_pressure_plate",
        71: "iron_door",
        72: "oak_pressure_plate",
        73: "redstone_ore",
        74: "lit_redstone_ore",
        75: "unlit_redstone_torch",
        76: "redstone_torch",
        77: "stone_button",
        78: "snow_layer",
        79: "ice",
        80: "snow",
        81: "cactus",
        82: "clay",
        83: "sugar_cane",
        84: "jukebox",
        85: "oak_fence",
        86: "pumpkin",
        87: "netherrack",
        88: "soul_sand",
        89: "glowstone",
        90: "nether_portal",
        91: "lit_pumpkin",
        92: "cake",
        93: "unpowered_repeater",
        94: "powered_repeater",
        95: "stained_glass",
        96: "oak_trapdoor",
        97: "silverfish_stone",
        98: "stone_bricks",
        99: "brown_mushroom_block",
        100: "red_mushroom_block",
        101: "iron_bars",
        102: "glass_pane",
        103: "melon_block",
        104: "pumpkin_stem",
        105: "melon_stem",
        106: "vine",
        107: "oak_fence_gate",
        108: "brick_stairs",
        109: "stone_brick_stairs",
        110: "mycelium",
        111: "waterlily",
        112: "nether_brick",
        113: "nether_brick_fence",
        114: "nether_brick_stairs",
        115: "nether_wart",
        116: "enchanting_table",
        117: "brewing_stand",
        118: "cauldron",
        119: "end_portal_frame",
        120: "end_stone",
        121: "end_rod",
        122: "dragon_egg",
        123: "redstone_lamp",
        124: "lit_redstone_lamp",
        125: "double_wooden_slab",
        126: "wooden_slab",
        127: "cocoa",
        128: "sandstone_stairs",
        129: "emerald_ore",
        130: "ender_chest",
        131: "tripwire_hook",
        132: "tripwire",
        133: "emerald_block",
        134: "spruce_stairs",
        135: "birch_stairs",
        136: "jungle_stairs",
        137: "command_block",
        138: "beacon",
        139: "cobblestone_wall",
        140: "flower_pot",
        141: "carrots",
        142: "potatoes",
        143: "wooden_button",
        144: "skull",
        145: "anvil",
        146: "trapped_chest",
        147: "weighted_pressure_plate_light",
        148: "weighted_pressure_plate_heavy",
        149: "unpowered_comparator",
        150: "powered_comparator",
        151: "daylight_detector",
        152: "redstone_block",
        153: "quartz_ore",
        154: "hopper",
        155: "quartz_block",
        156: "quartz_stairs",
        157: "activator_rail",
        158: "dropper",
        159: "stained_hardened_clay",
        160: "stained_glass_pane",
        161: "leaves2",
        162: "log2",
        163: "acacia_stairs",
        164: "dark_oak_stairs",
        165: "slime_block",
        166: "barrier",
        167: "iron_trapdoor",
        168: "prismarine",
        169: "sea_lantern",
        170: "hay_block",
        171: "carpet",
        172: "hardened_clay",
        173: "coal_block",
        174: "packed_ice",
        175: "double_plant",
        176: "standing_banner",
        177: "wall_banner",
        178: "daylight_detector_inverted",
        179: "red_sandstone",
        180: "red_sandstone_stairs",
        181: "double_stone_slab2",
        182: "stone_slab2",
        183: "spruce_fence_gate",
        184: "birch_fence_gate",
        185: "jungle_fence_gate",
        186: "dark_oak_fence_gate",
        187: "acacia_fence_gate",
        188: "spruce_fence",
        189: "birch_fence",
        190: "jungle_fence",
        191: "dark_oak_fence",
        192: "acacia_fence",
        193: "spruce_door",
        194: "birch_door",
        195: "jungle_door",
        196: "acacia_door",
        197: "dark_oak_door",
        198: "end_rod",
        199: "chorus_plant",
        200: "chorus_flower",
        201: "purpur_block",
        202: "purpur_pillar",
        203: "purpur_stairs",
        204: "purpur_double_slab",
        205: "purpur_slab",
        206: "end_stone_bricks",
        207: "beetroots",
        208: "grass_path",
        209: "end_gateway",
        210: "repeating_command_block",
        211: "chain_command_block",
        212: "frosted_ice",
        213: "magma_block",
        214: "nether_wart_block",
        215: "red_nether_brick",
        216: "bone_block",
        217: "structure_void",
        218: "observer",
        219: "shulker_box",
        220: "purple_shulker_box",
        221: "blue_shulker_box",
        222: "cyan_shulker_box",
        223: "light_gray_shulker_box",
        224: "gray_shulker_box",
        225: "pink_shulker_box",
        226: "lime_shulker_box",
        227: "yellow_shulker_box",
        228: "orange_shulker_box",
        229: "magenta_shulker_box",
        230: "light_blue_shulker_box",
        231: "white_shulker_box",
        232: "red_shulker_box",
        233: "green_shulker_box",
        234: "brown_shulker_box",
        235: "black_shulker_box",
    }

    @staticmethod
    def get_block_name_from_id(block_id):
        """Obté nom del bloc des de l'ID utilitzant constants de mcpi.block amb mapatge de fallback."""
        block_name = None
        
        try:
            from mcpi import block as mcblock
            # Primer provar constants de mcpi
            dict_items = list(mcblock.__dict__.items())
            
            i = 0
            while i < len(dict_items):
                name, obj = dict_items[i]
                
                # Verificar si és un bloc i té el mateix ID
                is_block = isinstance(obj, mcblock.Block)
                if is_block:
                    has_same_id = False
                    if obj.id == block_id:
                        has_same_id = True
                    
                    if has_same_id:
                        block_name = name.lower()
                        break
                
                i = i + 1
        except Exception:
            pass
        
        # Si no s'ha trobat, utilitzar mapatge local
        if block_name is None:
            # Buscar al diccionari local
            block_exists = False
            for key in GridMining.BLOCK_ID_NAMES.keys():
                if key == block_id:
                    block_exists = True
                    break
            
            if block_exists:
                block_name = GridMining.BLOCK_ID_NAMES[block_id]
            else:
                # Nom genèric si no es troba
                block_name = f"block_{block_id}"
        
        return block_name

    def get_name(self):
        return "grid"

    def mine(self, miner, material, amount):
        """
        Mina un cub 5x5x5 centrat a la posició inicial, capa per capa cap avall.
        
        Patró (vista superior):
        . . . . .
        . . . . .
        . . X . .   <- centre
        . . . . . 
        . . . . .
        
        Després mina 5 capes cap avall des del centre.
        
        Args:
            miner: MinerAgent amb client mc i inventari
            material: Material primari en què enfocar-se
            amount: Quants blocs minar en total
            
        Returns:
            Dict de {nom_material: comptador} de tots els blocs minats
        """
        mc = miner.mc
        coords = miner.mining_coords

        # Obtenir posició inicial
        if coords is not None:
            x, y, z = coords
        else:
            pos = mc.player.getTilePos()
            x, y, z = pos.x, pos.y, pos.z

        # Inicialitzar diccionari per seguiment de materials
        mined_materials = dict()
        total_mined = 0
        grid_size = 5  # 5x5 horitzontal
        depth = 5     # 5 capes de profunditat
        radius = grid_size // 2  # 2 blocs des del centre en cada direcció

        mc.postToChat(f"[Miner] Minant cub {grid_size}x{grid_size}x{depth} centrat a ({x}, {y}, {z})")

        # Minar capa per capa cap avall
        dy = 0
        while dy < depth:
            current_y = y - dy  # Baixar capa per capa
            
            # No minar per sota del bedrock
            if current_y < 1:
                break

            # Minar quadrícula 5x5 a aquesta capa
            dx = -radius
            while dx <= radius:
                dz = -radius
                while dz <= radius:
                    # Verificar si ja s'ha minat prou
                    if total_mined >= amount:
                        break

                    current_x = x + dx
                    current_z = z + dz

                    try:
                        current_block = mc.getBlock(current_x, current_y, current_z)

                        # Saltar aire, aigua, lava, bedrock
                        is_air = False
                        if current_block <= 0:
                            is_air = True
                        
                        is_liquid_or_bedrock = False
                        liquids_and_bedrock = [7, 8, 9, 10, 11]
                        i = 0
                        while i < len(liquids_and_bedrock):
                            if current_block == liquids_and_bedrock[i]:
                                is_liquid_or_bedrock = True
                                break
                            i = i + 1
                        
                        if not is_air and not is_liquid_or_bedrock:
                            # Minar qualsevol bloc sòlid trobat - obtenir nom dinàmicament des de l'ID del bloc
                            mat_name = self.get_block_name_from_id(current_block)
                            
                            # Trencar el bloc
                            mc.setBlock(current_x, current_y, current_z, 0)
                            
                            # Afegir a l'inventari (crea automàticament nova entrada si no existeix)
                            miner.inventory.add(mat_name, 1)
                            
                            # Actualitzar comptador de materials minats
                            material_count = 0
                            if mat_name in mined_materials:
                                material_count = mined_materials[mat_name]
                            mined_materials[mat_name] = material_count + 1
                            
                            total_mined = total_mined + 1

                            # Actualització de progrés cada 5 blocs
                            if total_mined % 5 == 0:
                                time.sleep(0.02)

                    except Exception as e:
                        miner.log.error(f"Error minant a ({current_x}, {current_y}, {current_z}): {e}")
                        # Continuar amb el següent bloc
                        pass

                    dz = dz + 1
                
                # Verificar si ja s'ha minat prou abans de continuar amb la següent columna
                if total_mined >= amount:
                    break
                
                dx = dx + 1

            # Verificar si ja s'ha minat prou abans de continuar amb la següent capa
            if total_mined >= amount:
                break
            
            dy = dy + 1

        return mined_materials
