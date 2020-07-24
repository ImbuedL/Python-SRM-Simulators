from copy import copy
import itertools
import numpy as np
 
"""
 
- This script does NOT handle spawners (except for rupee clusters)
- This script does NOT handle scarecrow memory leak
 
- This script does not account for ISoT memory leak for solution options
 
 
FOR DEKU PALACE, THIS DOES NOT ACCOUNT FOR POTENTIALLY NEEDING TO BREAK A POT FOR THE SUPERSLIDE
 
THIS SCRIPT DOES NOT ACCOUNT FOR GOLD SKULLTULA TOKENS
 
 
"""
 
 
"""
 
Note: Node size is 0x10 = 16 on English and 0x30 = 48 on JP
 
"""
 
version = 'English'
 
if version == 'English':
    node_size = 0x10
elif version == 'JP':
    nodesize = 0x30
else:
    print('Error: Invalid Version (choose "English" or "JP" )')
 
 
 
class Actor:
   
    """
   
   name: name of the actor, some string
   
   Id: Actor id, string of 4 integers
   
   size: the size of an actor instance for this actor (number of bytes, in decimal)
   
   category: the actor category (category 5 is treated differently than others)
             For now, giving everything not category 5 a category of 0
 
   overlay_type: determines where the AF loads in the heap
   
   unloadable: a boolean for whether or not it is possible to deallocate this actor without changing rooms
   
   address: the memory address of the actor in decimal (can convert to a hex string for output)
            Note: The earliest address we handle is 0x40B150 = 4239696. All addresses must be multiples of 16
           
   room_number: the number of the room these actors are associated with; if the actor is a transition (i..e Plane
               or Door), then set room_numer = False
               
   
   priority: an index to differentiate copies of the same instance
   
   from_spawner: True or False (True if it is from a spawner, like rupees from a cluster; False otherwise)
   
   transition: False is the actor is not a Loading Plane or a Door. Otherwise, it is a list of the rooms that the transition actor connects, ordered from least to greatest room number
   
   clearable: True if it is possible to set a flag to make this actor not respawn upon reloading the room (though, unless it it Category 5, it will attempt to reload and then immediately deallocate), False otherwise
   
   cleared: True if the flag was set to clear this actor, False otherwise
   
   """
   
    def __init__(self, name, Id, size, category, overlay_type, unloadable, address, room_number, priority, from_spawner, transition, clearable, cleared):
        self.name = name
        self.Id = Id
        self.size = size
        self.category = category
        self.overlay_type = overlay_type
        self.unloadable = unloadable
        self.address = address
        self.room_number = room_number
        self.priority = priority
        self.from_spawner = from_spawner
        self.transition = transition
        self.clearable = clearable
        self.cleared = cleared
 
class Room:
   
    """
   
   number: the room number (i.e. Room 0 has number 0)
   
   priority_queue: this will be the list of actor instances of the room, in order
   
   clock_exists: boolean for whether or not the clock is an actor in the queue
   
   clock_priority: if clock_exists == False, then clock_priority will be a number
                   to determine where in the queue the clock should be loaded, for
                   example, if clock_priority is 2, then it means that the clock
                   should be the 3rd actor to appear in the queue (first index is 0)
   
   """
   
    def __init__(self, number, priority_queue, clock_exists, clock_priority):
        self.number = number
        self.priority_queue = priority_queue
        self.clock_exists = clock_exists
        self.clock_priority = clock_priority
 
class Node:
   
    """
   address: which address in memory the node is at (as a base-10 integer for now)
   
   size: nodes should be 16 bytes (english), so input 16
   
   """
   
    def __init__(self, address, size):
        self.address = address
        self.size = size
 
class Overlay:
   
    def __init__(self, address, Id, size):
        self.address = address
        self.Id = Id
        self.size = size
 
 
"""
 
We define the Clock actor ahead of time as it is not necessarily present in each room
 
"""
 
 
Clock = Actor(name='Clock', Id='015A', size=340, category=0, overlay_type='A', unloadable=False, address=0, room_number=False, priority=0, from_spawner=False, transition=False, clearable=False, cleared=False)
 
###############################################################################
 
Oceanside_Room3_queue = [
        Actor(name='Loading Plane', Id='0018', size=332, category=0, overlay_type='B', unloadable=False, address=0, room_number=False, priority=0, from_spawner=False, transition=[3,4], clearable=False, cleared=False),
        Actor(name='Wooden Door', Id='0005', size=0x1CC, category=0, overlay_type='B', unloadable=False, address=0, room_number=False, priority=0, from_spawner=False, transition=[2,3], clearable=False, cleared=False),
        Actor(name='Stalchild (Oceanside Spider House)', Id='02A5', size=0x3EC, category=0, overlay_type='A', unloadable=True, address=0, room_number=3, priority=0, from_spawner=False, transition=False, clearable=False, cleared=False),
        Actor(name='Stalchild (Oceanside Spider House)', Id='02A5', size=0x3EC, category=0, overlay_type='A', unloadable=True, address=0, room_number=3, priority=1, from_spawner=False, transition=False, clearable=False, cleared=False),
        Actor(name='Stalchild (Oceanside Spider House)', Id='02A5', size=0x3EC, category=0, overlay_type='A', unloadable=True, address=0, room_number=3, priority=2, from_spawner=False, transition=False, clearable=False, cleared=False),
        Actor(name='Stalchild (Oceanside Spider House)', Id='02A5', size=0x3EC, category=0, overlay_type='A', unloadable=True, address=0, room_number=3, priority=3, from_spawner=False, transition=False, clearable=False, cleared=False),
        Actor(name='Pot', Id='0082', size=0x19C, category=0, overlay_type='A', unloadable=True, address=0, room_number=3, priority=0, from_spawner=False, transition=False, clearable=False, cleared=False),
        Actor(name='Pot', Id='0082', size=0x19C, category=0, overlay_type='A', unloadable=True, address=0, room_number=3, priority=1, from_spawner=False, transition=False, clearable=False, cleared=False),
        Actor(name='Oceanside Spider House Skull Kid Painting', Id='0210', size=0x244, category=0, overlay_type='A', unloadable=False, address=0, room_number=3, priority=0, from_spawner=False, transition=False, clearable=False, cleared=False),
        Actor(name='Oceanside Spider House Skull Kid Painting', Id='0210', size=0x244, category=0, overlay_type='A', unloadable=False, address=0, room_number=3, priority=1, from_spawner=False, transition=False, clearable=False, cleared=False),
        Actor(name='Oceanside Spider House Skull Kid Painting', Id='0210', size=0x244, category=0, overlay_type='A', unloadable=False, address=0, room_number=3, priority=2, from_spawner=False, transition=False, clearable=False, cleared=False),
        Actor(name='Oceanside Spider House Skull Kid Painting', Id='0210', size=0x244, category=0, overlay_type='A', unloadable=False, address=0, room_number=3, priority=3, from_spawner=False, transition=False, clearable=False, cleared=False),
        Actor(name='Gold Skulltula', Id='0050', size=0x4A4, category=0, overlay_type='A', unloadable=True, address=0, room_number=3, priority=0, from_spawner=False, transition=False, clearable=True, cleared=False),
        Actor(name='Spiderweb', Id='0125', size=0x2FC, category=0, overlay_type='A', unloadable=True, address=0, room_number=3, priority=0, from_spawner=False, transition=False, clearable=True, cleared=False),
        Actor(name='Gold Skulltula', Id='0050', size=0x4A4, category=0, overlay_type='A', unloadable=True, address=0, room_number=3, priority=1, from_spawner=False, transition=False, clearable=True, cleared=False),
        Actor(name='Bonk Actor (01E7)', Id='01E7', size=0x148, category=0, overlay_type='A', unloadable=True, address=0, room_number=3, priority=0, from_spawner=False, transition=False, clearable=False, cleared=False),
        Actor(name='Gold Skulltula', Id='0050', size=0x4A4, category=0, overlay_type='A', unloadable=True, address=0, room_number=3, priority=2, from_spawner=False, transition=False, clearable=True, cleared=False),
        Actor(name='Bonk Actor (01E7)', Id='01E7', size=0x148, category=0, overlay_type='A', unloadable=True, address=0, room_number=3, priority=1, from_spawner=False, transition=False, clearable=False, cleared=False),
        Actor(name='Gold Skulltula', Id='0050', size=0x4A4, category=0, overlay_type='A', unloadable=True, address=0, room_number=3, priority=3, from_spawner=False, transition=False, clearable=True, cleared=False),
        Actor(name='Bonk Actor (01E7)', Id='01E7', size=0x148, category=0, overlay_type='A', unloadable=True, address=0, room_number=3, priority=2, from_spawner=False, transition=False, clearable=False, cleared=False),
        Actor(name='Tent-Shaped Spider Web', Id='01F4', size=0x3CC, category=0, overlay_type='A', unloadable=True, address=0, room_number=3, priority=0, from_spawner=False, transition=False, clearable=True, cleared=False),
        Actor(name='Oceanside Spider House Fireplace Grate', Id='020F', size=0x284, category=0, overlay_type='A', unloadable=False, address=0, room_number=3, priority=0, from_spawner=False, transition=False, clearable=False, cleared=False),
        Actor(name='Gold Skulltula', Id='0050', size=0x4A4, category=0, overlay_type='A', unloadable=True, address=0, room_number=3, priority=4, from_spawner=False, transition=False, clearable=True, cleared=False),
        Actor(name='Bonk Actor (01E7)', Id='01E7', size=0x148, category=0, overlay_type='A', unloadable=True, address=0, room_number=3, priority=3, from_spawner=False, transition=False, clearable=False, cleared=False)
        ]
 
 
Oceanside_Room4_queue = [
        Oceanside_Room3_queue[0],
        Actor(name='Skulltula', Id='0024', size=0x550, category=5, overlay_type='A', unloadable=True, address=0, room_number=4, priority=0, from_spawner=False, transition=False, clearable=False, cleared=False),
        Actor(name='Chest', Id='0006', size=548, category=0, overlay_type='A', unloadable=False, address=0, room_number=4, priority=0, from_spawner=False, transition=False, clearable=False, cleared=False)
        ]
 
 
 
 
 
###############################################################################
 
Room0_queue = [
        Actor(name='Wooden Door', Id='0005', size=460, category=0, overlay_type='B', unloadable=False, address=0, room_number=False, priority=0, from_spawner=False, transition=[0,3], clearable=False, cleared=False),
        Actor(name='Loading Plane', Id='0018', size=332, category=0, overlay_type='B', unloadable=False, address=0, room_number=False, priority=0, from_spawner=False, transition=[0,1], clearable=False, cleared=False),
        Actor(name='Rupee Cluster', Id='00E8', size=360, category=0, overlay_type='A', unloadable=True, address=0, room_number=0, priority=0, from_spawner=False, transition=False, clearable=True, cleared=False),
        Actor(name='Dripping Water Effect', Id='0170', size=3644, category=0, overlay_type='A', unloadable=False, address=0, room_number=0, priority=0, from_spawner=False, transition=False, clearable=False, cleared=False),
        Actor(name='Dripping Water Effect', Id='0170', size=3644, category=0, overlay_type='A', unloadable=False, address=0, room_number=0, priority=1, from_spawner=False, transition=False, clearable=False, cleared=False),
        Actor(name='Torch Stand (Generic)', Id='0039', size=500, category=0, overlay_type='A', unloadable=False, address=0, room_number=0, priority=0, from_spawner=False, transition=False, clearable=False, cleared=False),
        Actor(name='Pot', Id='0082', size=412, category=0, overlay_type='A', unloadable=True, address=0, room_number=0, priority=0, from_spawner=False, transition=False, clearable=False, cleared=False),
        Actor(name='Pot', Id='0082', size=412, category=0, overlay_type='A', unloadable=True, address=0, room_number=0, priority=1, from_spawner=False, transition=False, clearable=False, cleared=False),
        Actor(name='Pot', Id='0082', size=412, category=0, overlay_type='A', unloadable=True, address=0, room_number=0, priority=2, from_spawner=False, transition=False, clearable=False, cleared=False),
        Actor(name='???0158', Id='0158', size=328, category=0, overlay_type='A', unloadable=False, address=0, room_number=0, priority=0, from_spawner=False, transition=False, clearable=False, cleared=False)
        ]
 
 
Room1_queue = [
        Actor(name='Door Shutter', Id='001E', size=360, category=0, overlay_type='B', unloadable=False, address=0, room_number=False, priority=0, from_spawner=False, transition=[1,2], clearable=False, cleared=False),
        Room0_queue[1],
        Actor(name='Bad Bat', Id='015B', size=476, category=5, overlay_type='A', unloadable=True, address=0, room_number=1, priority=0, from_spawner=False, transition=False, clearable=True, cleared=False),
        Actor(name='Bad Bat', Id='015B', size=476, category=5, overlay_type='A', unloadable=True, address=0, room_number=1, priority=1, from_spawner=False, transition=False, clearable=True, cleared=False),
        Actor(name='Bad Bat', Id='015B', size=476, category=5, overlay_type='A', unloadable=True, address=0, room_number=1, priority=2, from_spawner=False, transition=False, clearable=True, cleared=False),
        Actor(name='Bad Bat', Id='015B', size=476, category=5, overlay_type='A', unloadable=True, address=0, room_number=1, priority=3, from_spawner=False, transition=False, clearable=True, cleared=False),
        Actor(name='Bad Bat', Id='015B', size=476, category=5, overlay_type='A', unloadable=True, address=0, room_number=1, priority=4, from_spawner=False, transition=False, clearable=True, cleared=False),
        Actor(name='Bad Bat', Id='015B', size=476, category=5, overlay_type='A', unloadable=True, address=0, room_number=1, priority=5, from_spawner=False, transition=False, clearable=True, cleared=False),
        Actor(name='Bad Bat', Id='015B', size=476, category=5, overlay_type='A', unloadable=True, address=0, room_number=1, priority=6, from_spawner=False, transition=False, clearable=True, cleared=False),
        Actor(name='Bad Bat', Id='015B', size=476, category=5, overlay_type='A', unloadable=True, address=0, room_number=1, priority=7, from_spawner=False, transition=False, clearable=True, cleared=False),
        Actor(name='Bad Bat', Id='015B', size=476, category=5, overlay_type='A', unloadable=True, address=0, room_number=1, priority=8, from_spawner=False, transition=False, clearable=True, cleared=False),
        Actor(name='Bad Bat', Id='015B', size=476, category=5, overlay_type='A', unloadable=True, address=0, room_number=1, priority=9, from_spawner=False, transition=False, clearable=True, cleared=False),
        Actor(name='Bad Bat', Id='015B', size=476, category=5, overlay_type='A', unloadable=True, address=0, room_number=1, priority=10, from_spawner=False, transition=False, clearable=True, cleared=False),
        Actor(name='Bad Bat', Id='015B', size=476, category=5, overlay_type='A', unloadable=True, address=0, room_number=1, priority=11, from_spawner=False, transition=False, clearable=True, cleared=False),
        Actor(name='Bad Bat', Id='015B', size=476, category=5, overlay_type='A', unloadable=True, address=0, room_number=1, priority=12, from_spawner=False, transition=False, clearable=True, cleared=False),
        Actor(name='Bad Bat', Id='015B', size=476, category=5, overlay_type='A', unloadable=True, address=0, room_number=1, priority=13, from_spawner=False, transition=False, clearable=True, cleared=False),
        Actor(name='Bad Bat', Id='015B', size=476, category=5, overlay_type='A', unloadable=True, address=0, room_number=1, priority=14, from_spawner=False, transition=False, clearable=True, cleared=False),
        Actor(name='Bad Bat', Id='015B', size=476, category=5, overlay_type='A', unloadable=True, address=0, room_number=1, priority=15, from_spawner=False, transition=False, clearable=True, cleared=False),
        Actor(name='Bad Bat', Id='015B', size=476, category=5, overlay_type='A', unloadable=True, address=0, room_number=1, priority=16, from_spawner=False, transition=False, clearable=True, cleared=False),
        Actor(name='Bad Bat', Id='015B', size=476, category=5, overlay_type='A', unloadable=True, address=0, room_number=1, priority=17, from_spawner=False, transition=False, clearable=True, cleared=False),
        Actor(name='Bad Bat', Id='015B', size=476, category=5, overlay_type='A', unloadable=True, address=0, room_number=1, priority=18, from_spawner=False, transition=False, clearable=True, cleared=False),
        Actor(name='Bad Bat', Id='015B', size=476, category=5, overlay_type='A', unloadable=True, address=0, room_number=1, priority=19, from_spawner=False, transition=False, clearable=True, cleared=False),
        Actor(name='Torch Stand (Generic)', Id='0039', size=500, category=0, overlay_type='A', unloadable=False, address=0, room_number=1, priority=0, from_spawner=False, transition=False, clearable=False, cleared=False),
        Actor(name='Torch Stand (Generic)', Id='0039', size=500, category=0, overlay_type='A', unloadable=False, address=0, room_number=1, priority=1, from_spawner=False, transition=False, clearable=False, cleared=False),
        Actor(name='Torch Stand (Generic)', Id='0039', size=500, category=0, overlay_type='A', unloadable=False, address=0, room_number=1, priority=2, from_spawner=False, transition=False, clearable=False, cleared=False),
        Actor(name='Pot', Id='0082', size=412, category=0, overlay_type='A', unloadable=True, address=0, room_number=1, priority=0, from_spawner=False, transition=False, clearable=False, cleared=False),
        Actor(name='Pot', Id='0082', size=412, category=0, overlay_type='A', unloadable=True, address=0, room_number=1, priority=1, from_spawner=False, transition=False, clearable=False, cleared=False),
        Actor(name='Pot', Id='0082', size=412, category=0, overlay_type='A', unloadable=True, address=0, room_number=1, priority=2, from_spawner=False, transition=False, clearable=False, cleared=False),
        Actor(name='Chest', Id='0006', size=548, category=0, overlay_type='A', unloadable=False, address=0, room_number=1, priority=0, from_spawner=False, transition=False, clearable=False, cleared=False)
        ]
 
###############################################################################
 
Room0 = Room(0, Room0_queue, False, 2)
Room1 = Room(1, Room1_queue, False, 2)
 
 
Oceanside_Room3 = Room(3, Oceanside_Room3_queue, False, 2)
Oceanside_Room4 = Room(4, Oceanside_Room4_queue, False, 1)
 
"""
 
Define the list of Rooms that we consider
 
"""
 
Room_List = [Room0, Room1]
 
Oceanside_Room_List = [Oceanside_Room3, Oceanside_Room4]
 
 
"""
 
In Overlay_dict we collect all of the Overlays of Type A, where the keys are
the corresponding actor ids
 
"""
 
# NOTE: This must be named "Overlay_dict" because it is hardcoded in some functions, like the Deallocate() function
Overlay_dict = {
        '015A' : Overlay(address=0, Id='015A', size=6000),
        '00E8' : Overlay(address=0, Id='00E8', size=1984),
        '0170' : Overlay(address=0, Id='0170', size=10688),
        '0039' : Overlay(address=0, Id='0039', size=3552),
        '0082' : Overlay(address=0, Id='0082', size=9040),
        '0158' : Overlay(address=0, Id='0158', size=1104),
        '015B' : Overlay(address=0, Id='015B', size=6048),
        '0006' : Overlay(address=0, Id='0006', size=8640),
        '0017' : Overlay(address=0, Id='0017', size=10432),
        '017B' : Overlay(address=0, Id='017B', size=14320),
        '007B' : Overlay(address=0, Id='007B', size=5104),
        '00A2' : Overlay(address=0, Id='00A2', size=24448),
        '02A5' : Overlay(address=0, Id='02A5', size=0x2660),
        '0210' : Overlay(address=0, Id='0210', size=0xB90),
        '0050' : Overlay(address=0, Id='0050', size=0x3540),
        '0125' : Overlay(address=0, Id='0125', size=0x1490),
        '01E7' : Overlay(address=0, Id='01E7', size=0x450),
        '01F4' : Overlay(address=0, Id='01F4', size=0x1A80),
        '020F' : Overlay(address=0, Id='020F', size=0x780),
        '0024' : Overlay(address=0, Id='0024', size=0x28E0),
        '00E3' : Overlay(address=0, Id='00E3', size=0x420)
            }
 
"""
 
Here we collect a list of the actors that we allow ourselves to spawn
 
Notes:
   'Zora Fins' means 2 fins
   'Bugs' means a set of 3 bugs
   
 
"""
 
Allocation_List = [
        'Nothing',
        'Bomb',
        'Smoke',
        'Arrow',
        'Hookshot',
        'Charged Spin Attack',
        'Chu',
        'Zora Fins',
        'Fish',
        'Bugs'
        ]
 
######
 
 
"""
 
NOTE: We NEED to have 'Hookshot' and 'Charged Spin Attack' as the last two options
in order to consider all cases
 
Don't have 'Bomb' before 'Smoke' to ensure that the Smoke always gets allocated first
 
maybe in the future you could jumble/randomize the order of things in this list at each step
of the solver
 
"""
Hardcoded_Allocation_List = [
        'Smoke',
        'Smoke',
        'Smoke',
        'Chu',
        'Chu',
        'Chu',
        'Arrow',
        'Arrow',
        'Arrow',
        'Arrow',
        'Arrow',
        'Bomb',
        'Bomb',
        'Bomb',
        'Zora Fins',
        'Fish',
        'Fish',
        'Bugs',
        'Bugs',
        'Hookshot',
        'Charged Spin Attack'
        ]
 
"""
 
Here we collect a list of the Ids grabbable actors that we can use for superslide SRM
So far this includes:
   
   0082: Pot
 
"""
 
Grabbable_Actors = ['0082']
 
 
"""
 
Here we collect a list of Actor Ids for spawners. So far this includes:
   
   00E8: Rupee Cluster
 
"""
 
Spawner_Ids = ['00E8']
 
 
"""
 
We initialize the Heap as a list, putting a node with address 0x40B140 in the 0th entry
and we place a dummy node at the end of the Heap so that there will always exist two
consecutive nodes for us to define a condition for which free space in the Heap exists
 
Keep in mind that the 0x5FFFFF address in the dummy node will not reflect the actual
address of the corresponding node in-game, but it also isn't relevant to heap manipulation
since it is so far down
 
"""
 
 
Heap = [Node(0x40B140, node_size), Node(0x5FFFFF, node_size)]
 
 
 
def Overlay_In_Heap(Heap, overlay):
   
    """
   
   Overlay is the overlay that we want to check whether or not it is in the Heap
   
   This function will return True if Overlay is in the Heap and False otherwise
   
   """
   
    overlay_in_heap = False
   
    for entry in Heap:
       
        if type(entry) == Overlay and entry.Id == overlay.Id:
           
            overlay_in_heap = True
       
    return overlay_in_heap
 
 
def Actor_Id_In_Heap(Heap, actor_id):
   
    """
   
   actor_id is the Id that we want to check for
   
   This function will return True if there exists an Actor in the Heap that
   has actor_id as its Id and it will return False otherwise
   
   """
   
    actor_id_in_heap = False
   
    for entry in Heap:
       
        if type(entry) == Actor and entry.Id == actor_id:
           
            actor_id_in_heap = True
   
    return actor_id_in_heap
 
 
def Find_Gaps(Heap):
   
    """
   
   This function will find all consecutive nodes and output a list of 4-tuples
   where the first two entries correspond to the indices of each node in the list
   and the last two entries correspond to the addresses of each node
   
   The list should be in order, from the start of the Heap to the end of the Heap
   
   """
   
    consecutive_node_count = 0
   
    node_1_address = 0
    node_2_address = 0
    node_1_index = 0
    node_2_index = 0
   
    consecutive_node_list = []
    for entry in Heap:
        if type(entry) == Node and consecutive_node_count == 0:
            node_1_address = entry.address
            node_1_index = Heap.index(entry)
            consecutive_node_count += 1
        elif type(entry) == Node and consecutive_node_count == 1:
            node_2_address = entry.address
            node_2_index = Heap.index(entry)
           
            consecutive_node_list.append((node_1_index, node_2_index, node_1_address, node_2_address))
           
            consecutive_node_count += 1
        elif type(entry) != Node:
            consecutive_node_count = 0
        elif type(entry) == Node and consecutive_node_count > 1:
            consecutive_node_count += 1
            print("ERROR: More than 2 consecutive nodes!! (Find_Gaps() Error Message)")
       
   
    return consecutive_node_list
   
 
 
 
def Allocate(Heap, actor, Overlay_Dict):
   
    """
   
   actor is the actor that we want to allocate into the Heap
   
   Overlay_Dict is a dictionary where the keys are the actor ids which point to the corresponding Overlays
   
   This function will account for placing nodes and overlays
   
   """
   
   
    #Overlay = Overlay_Dict[actor.Id]
   
    #Overlay_Allocated = False
   
    #if Overlay_In_Heap(Heap, Overlay) == True:
    #    Overlay_Allocated = True
   
    Actor_Allocated = False
   
    """
   ##### Not yet defined, not sure if I will bother; not really necessary. Probably should for debugging
   if Actor_In_Heap == True:
       print('Error: This Actor is already allocated!! (Error message from Allocate() function)')
   """
   
    gap_list = Find_Gaps(Heap)
   
    # Because we initialize the Heap with 2 nodes, there should always be at least one gap
    if len(gap_list) < 1:
        print('ERROR: len(gap_list) < 1 in Allocate() function')
   
   
    # If the Overlay is type A and the Overlay is not already in the Heap, then we want to allocate the overlay first
    if actor.overlay_type == 'A':
       
        ##### We only define Overlay for Type A overlays because Overlay_Dict only has Type A overlays
        Overlay = Overlay_Dict[actor.Id]
        Overlay_Allocated = False
       
        if Overlay_In_Heap(Heap, Overlay) == True:
            Overlay_Allocated = True
       
       
        if Overlay_In_Heap(Heap, Overlay) == False:
       
            for gap in gap_list:
               
                if Overlay_Allocated == True:
                    break ##### This ensures we don't add in the same Overlay multiple times
               
                node_2_index = gap[1]
                node_1_address = gap[2]
                node_2_address = gap[3]
               
                gap_size = node_2_address - node_1_address - node_size
               
                ##### Case 1: the Overlay can fit, but there is NOT enough space for an extra node
                # Note that gap_size is always a multiple of 16
               
                if Overlay.size <= gap_size and Overlay.size > gap_size - 2*node_size:
                   
                    Overlay.address = node_1_address + node_size
                    Heap.insert(node_2_index, Overlay)
                    Overlay_Allocated = True
                   
               
                ##### Case 2: the Overlay can fit and a new node can also fit
               
                elif Overlay.size <= gap_size and Overlay.size <= gap_size - 2*node_size:
                   
                    Overlay.address = node_1_address + node_size
                    Heap.insert(node_2_index, Overlay)
                   
                    ########### ADD IN THE NODE HERE
                    if Overlay.size%16 > 0:
                        Heap.insert(node_2_index + 1, Node(address=Overlay.address + Overlay.size + (16 - Overlay.size%16), size=node_size))
                    elif Overlay.size%16 == 0:
                        Heap.insert(node_2_index + 1, Node(address=Overlay.address + Overlay.size, size=node_size))
                       
                    Overlay_Allocated = True
               
    ############ Now the overlay (if applicable) has been allocated. Now we need to allocate the actor.
   
    ##### We need to update the gaps_list to account for the overlay being allocated in the Heap already
    gap_list = Find_Gaps(Heap)
   
    for gap in gap_list:
       
        if Actor_Allocated == True:
            break ##### This ensures we don't add in the same Actor multiple times
       
        node_2_index = gap[1]
        node_1_address = gap[2]
        node_2_address = gap[3]
       
        gap_size = node_2_address - node_1_address - node_size
       
        ##### Case 1: the Actor can fit, but there is NOT enough space for an extra node
        # Note that gap_size is always a multiple of 16
       
        if actor.size <= gap_size and actor.size > gap_size - 2*node_size:
           
            actor.address = node_1_address + node_size
            Heap.insert(node_2_index, actor)
            Actor_Allocated = True
           
       
        ##### Case 2: the Actor can fit and a new node can also fit
       
        elif actor.size <= gap_size and actor.size <= gap_size - 2*node_size:
           
            actor.address = node_1_address + node_size
            Heap.insert(node_2_index, actor)
           
            ########### ADD IN THE NODE HERE
            if actor.size%16 > 0:
                Heap.insert(node_2_index + 1, Node(address=actor.address + actor.size + (16 - actor.size%16), size=node_size))
            elif actor.size%16 == 0:
                Heap.insert(node_2_index + 1, Node(address=actor.address + actor.size, size=node_size))
                   
            Actor_Allocated = True
 
def Borders_Node(Heap, entry):
   
    """
   
   This function takes an entry of the Heap as input and determines whether or
   not this entry is adjacent to a node in the heap (the purpose of this is to
   check if a node is bordering another node since actors and overlays should
   be bordering two nodes under every circumstance)
   
   Returns True if the entry is bordering a node, returns False otherwise    
   
   """
   
    borders_node = False
   
    entry_index = Heap.index(entry)
   
    border_1_is_node = False
    border_2_is_node = False
   
    if entry_index != 0:
        border_1 = Heap[entry_index - 1]
        if type(border_1) == Node:
            border_1_is_node = True
   
    if entry_index != len(Heap) - 1:
        border_2 = Heap[entry_index + 1]
        if type(border_2) == Node:
            border_2_is_node = True
   
    if border_1_is_node == True or border_2_is_node == True:
        borders_node = True
   
    return borders_node
       
 
 
def Deallocate(Heap, actor, Overlay_dict):
   
   
    """
   
   actor is the actor that we want to be deallocated from the Heap
   
   This function will account for removing nodes and overlays
   
   ##### Remove the actor AND node if applicable
   ##### Check if any actors with the same Id are still in the Heap
   ##### if not (and the actor has overlay Type A), then remove the overlay
   
   We only remove a node if it is part of a gap before deallocating the actor
   That is, we only remove a node if it borders another node before the actor is deallocated
   
   """
   
    if type(actor) != Actor:
        print("ERROR: Attempted to deallocate something other than an Actor (Deallocate() function error message)")
   
    # The index of where the actor is in the Heap before being deallocated; this will change after we remove the first node
    actor_index = Heap.index(actor)
   
    ##### First check the node above the actor in the Heap
    node_1 = Heap[actor_index - 1]
    if type(node_1) != Node:
        print("ERROR: One of the nodes is not actually a node! (Deallocate() function error message)")
   
    if Borders_Node(Heap, node_1) == True:
        Heap.remove(node_1)
       
    ########## Now the first node has been removed and the indices of the Heap shift
   
    ##### Now we check the node below the actor in the Heap
   
    # The index of where the actor is in the Heap before being deallocated; this will change after we remove the first node
    actor_index = Heap.index(actor)
   
    node_2 = Heap[actor_index + 1]
    if type(node_2) != Node:
        print("ERROR: One of the nodes is not actually a node! (Deallocate() function error message)")
   
    if Borders_Node(Heap, node_2) == True:
        Heap.remove(node_2)
   
    ###########################################################################
    ##### Now we have removed both of the nodes, if applicable and we must remove the actor itself
   
    Heap.remove(actor)
   
    """
   
   Now if the actor has a Type A overlay, then we must check if the Heap contains
   any other actors that have the same Id as actor and if not, then we must also
   remove its overlay from the Heap
   
   We must also account for removing the nodes around the overlay, if applicable
   
   """
   
    if actor.overlay_type == 'A' and Actor_Id_In_Heap(Heap, actor.Id) == False:
       
        ##### First check the node above the overlay
        overlay_index = Heap.index(Overlay_dict[actor.Id])
        node1 = Heap[overlay_index - 1]
       
        if type(node1) != Node:
            print("ERROR: One of the nodes is not actually a node! (Deallocate() function error message)")
       
        if Borders_Node(Heap, node1) == True:
            Heap.remove(node1)
       
       
        ##### Now we check the node below the overlay
        overlay_index = Heap.index(Overlay_dict[actor.Id])
        node2 = Heap[overlay_index + 1]
       
        if type(node2) != Node:
            print("ERROR: One of the nodes is not actually a node! (Deallocate() function error message)")
       
        if Borders_Node(Heap, node2) == True:
            Heap.remove(node2)
       
        ###########################################################################
        ##### Now we have removed both of the nodes, if applicable and we must remove the overlay itself
       
        Heap.remove(Overlay_dict[actor.Id])
 
 
 
def Load_Scene(Heap, room, Overlay_dict):
   
    if len(Heap) != 2:
        print("ERROR: Attempted to use Load_Scene() with an inappropriate Heap")
   
    entry_count = 0
    for entry in room.priority_queue:
       
        ##### If the clock is not in the room's set of actors, then we must allocate the clock at the appropriate time when we load the scene
        if entry_count == room.clock_priority and room.clock_exists == False:
           
            ##### Allocate the 3-Day Clock actor
            Allocate(Heap, Clock, Overlay_dict)
            entry_count += 1
       
        ##### Allocate the entry in the room's priority queue
        Allocate(Heap, entry, Overlay_dict)
       
        entry_count += 1
   
    ##### Now that all of the actors have been allocated, we want to add in all of the actors that the spawners spawn
   
    """
   
   NOTE: THIS DOES NOT HANDLE SPAWNERS OTHER THAN RUPEE CLUSTERS AT THE MOMENT
   
   In the future, it will need to be considered how the actors created by spawners
   prioritize over each other... Spring MV is maybe the only place where this really matters
   
   """
   
    ##### Check for Rupee Cluster
    if Overlay_In_Heap(Heap, Overlay_dict['00E8']) == True:
       
        for j in range(7):
            rupee = Actor(name='Collectible (Rupee from Rupee Cluster)', Id='000E', size=424, category=0, overlay_type='B', unloadable=True, address=0, room_number=room.number, priority=j, from_spawner=True, transition=False, clearable=True, cleared=False)
           
            Allocate(Heap, rupee, Overlay_dict)
 
 
 
def Actor_From_Room_In_Heap(Heap, Room_Number):
   
    """
   
   This function takes the Heap and the number of the Room in question as input
   It returns True if there exists an Actor in the Heap with the inputted Room_Number and False otherwise
   
   """
   
    actor_from_room_in_heap = False
   
    for entry in Heap:
       
        if type(entry) == Actor and entry.room_number is Room_Number:
           
            actor_from_room_in_heap = True
   
    return actor_from_room_in_heap
 
def Cleared_Actor_In_Heap(Heap):
   
    """
   
   This function returns True if there is a cleared actor in the Heap and False otherwise
   
   """
   
    cleared_actor_in_heap = False
   
    for entry in Heap:
       
        if type(entry) == Actor and entry.cleared == True:
           
            cleared_actor_in_heap = True
       
    return cleared_actor_in_heap
 
 
def Shared_Transition_Count(Heap, Room_Number_1, Room_Number_2):
   
    """
   
   This function returns the number of transitions (Planes/Doors) that are shared between
   the two rooms with room numbers Room_Number_1 and Room_Number_2
   
   """
   
    shared_transition_count = 0
   
    for entry in Heap:
       
        if type(entry) == Actor and entry.transition != False:
           
            if (entry.transition[0] == Room_Number_1 and entry.transition[1] == Room_Number_2) or (entry.transition[0] == Room_Number_2 and entry.transition[1] == Room_Number_1):
               
                shared_transition_count += 1
   
    return shared_transition_count
 
def Is_Shared_Transition(actor, Room_Number_1, Room_Number_2):
   
    """
   
   If actor is a transition shared between Rooms with numbers Room_Number_1 and Room_Number_2,
   then this function returns True. Otherwise it returns False
   
   """
   
    is_shared_transition = False
   
    if type(actor) == Actor and actor.transition != False:
       
        if (actor.transition[0] == Room_Number_1 and actor.transition[1] == Room_Number_2) or (actor.transition[0] == Room_Number_2 and actor.transition[1] == Room_Number_1):
           
            is_shared_transition = True
   
    return is_shared_transition
       
 
def Transition_Is_In_Room(actor, Room_Number):
   
    transition_is_in_room = False
   
    if type(actor) == Actor and actor.transition != False:
       
        if actor.transition[0] == Room_Number or actor.transition[1] == Room_Number:
           
            transition_is_in_room = True
   
    return transition_is_in_room
 
 
def Find_Clock_List(Heap):
   
    """
   
   This function finds all clock actor instances in the Heap and returns a list of them, in order
   
   """
   
    clock_list = []
   
    for entry in Heap:
       
        if type(entry) == Actor and entry.Id == '015A':
           
            clock_list.append(entry)
   
    return clock_list
   
 
def Load_Room(Heap, room, transition, Overlay_dict):
   
   
    """
   
   This function updates the Heap after you enter room through transition
   For example, you might enter Room0 through Plane1 or Door3
   
   Before executing the script, should probably define Plane1, Plane2, ...
   Door1, Door2, ..., etc. as the corresponding entries from the room queues.
   This will make the code more readable when looking for solutions
   
   
   * First we load all of the actors from the new room
   * Next, we deallocate everything (well, not literally everything...) from the previous room
   
   
   Things that this function needs to handle:
       
       - make sure that you check if each actor was cleared or not (if clearable == True, otherwise it isn't applicable)
       and then check if it is Category 5 to determine if it loads and immediately deallocates or not
       
       - checking which clock to deallocate (i.e. deallocate the one that comes later
       on in the Heap if there are more than one). Maybe define a Find_Clocks function
       
       - make sure transition never deallocates and never attempts to allocate
       
       - make sure that the other Transitions unload and then reload (if applicable) after all of
       the stuff from the previous room deallocated
       
       - when deallocating stuff from the room that isn't the room you're entering, be sure
       not to deallocate the clock. Also be careful of relevant Transitions as they don't have
       actual room numbers (replaced with False)
       
       - allocate stuff from spawners after the fact (even after planes)
       
   
   """
   
    if transition not in Heap:
        print('2222222222')
       
    if transition not in room.priority_queue:
        print('44444444')
   
    if (transition not in Heap) or (transition not in room.priority_queue):
        print("ERROR: Attempted to use Load_Room() with an invalid transition")
   
    current_room_number = -1
    new_room_number = room.number
   
    if transition.transition[0] == room.number:
        current_room_number = transition.transition[1]
    elif transition.transition[1] == room.number:
        current_room_number = transition.transition[0]
    else:
        print("ERROR: Error with transition list (Load_Room() error message)")
   
    """
   First we load all of the actors from the new room, EXCEPT for: the plane/door
   we pass through AND any other shared transitions AND any actors with both
   cleared == True and Category == 5 (these ones never attempt to load)
   """
   
    for actor in room.priority_queue:
       
        ### If the actor is not a Transition OR if the actor is a transition but doesn't connect to the current room
        if (actor.transition == False) or (actor.transition != False and actor.transition[0] != current_room_number and actor.transition[1] != current_room_number):
           
            ### If the actor is Category 5, then only attempt to load it if it has not been cleared
            if actor.category != 5 or actor.cleared == False:
               
                Allocate(Heap, actor, Overlay_dict)
   
    """
   - Now all of the relevant actors from the new room have been allocated
   - Now we need to immediately deallocate any actors with Clearable == True and Cleared == True
   - We also need to deallocate any transitions which are shared between the current room and the new room
     EXCEPT for transition itself (the transition that we passed through to get to the new room)
   - We also need to deallocate the second clock actor in the Heap if it exists (do this after everything else for simplicity)
     
     Note that "current_room_number" is the room number of the room we were in before loading the new room
   """
 
    while Actor_From_Room_In_Heap(Heap, current_room_number) == True or Cleared_Actor_In_Heap(Heap) == True or Shared_Transition_Count(Heap, current_room_number, new_room_number) > 1:
       
        for entry in Heap:
           
            if (type(entry) == Actor) and (entry.room_number is current_room_number or entry.cleared == True or Is_Shared_Transition(entry, current_room_number, new_room_number) == True or  (entry.transition != False and Transition_Is_In_Room(entry, new_room_number) == False )  ) and (entry != transition):
               
                Deallocate(Heap, entry, Overlay_dict)
   
    ########## Now we will find all of the clocks and deallocate the second clock if it exists (and report error if more than two clocks)
   
    Clock_List = Find_Clock_List(Heap)
   
    if len(Clock_List) > 2:
        print("ERROR: More than 2 Clocks in the Actor Heap (Load_Room() Error Message)")
    elif len(Clock_List) < 1:
        print("ERROR: No Clock Actor Instance in the Actor Heap (Load_Room() Error Message)")
   
    ##### If there are two clocks, then we deallocate the second clock that appears in the Heap
    if len(Clock_List) > 1:
       
        Deallocate(Heap, Clock_List[1], Overlay_dict)
   
   
    ##### Now we allocate any shared transitions EXCEPT for transition itself (the door/plane we entered to get into this room)
   
    for entry in room.priority_queue:
       
        # If entry is a shared transition and is NOT the transition that we passed through
        if (type(entry) == Actor) and (entry.transition != False) and Is_Shared_Transition(entry, current_room_number, new_room_number) == True and (entry != transition):
           
            Allocate(Heap, entry, Overlay_dict)
   
    ###################################### Now we only have to account for allocating things from spawners
   
   
    """
   
   NOTE: THIS DOES NOT HANDLE SPAWNERS OTHER THAN RUPEE CLUSTERS AT THE MOMENT
   
   In the future, it will need to be considered how the actors created by spawners
   prioritize over each other... Spring MV is maybe the only place where this really matters
   
   """
   
    ##### Check for Rupee Cluster
    if Overlay_In_Heap(Heap, Overlay_dict['00E8']) == True:
       
        for j in range(7):
            rupee = Actor(name='Collectible (Rupee from Rupee Cluster)', Id='000E', size=424, category=0, overlay_type='B', unloadable=True, address=0, room_number=room.number, priority=j, from_spawner=True, transition=False, clearable=True, cleared=False)
           
            Allocate(Heap, rupee, Overlay_dict)
       
 
 
 
 
def Display_Heap(Heap):
   
    for entry in Heap:
       
        if type(entry) == Node:
           
            print(hex(entry.address) + '-----' + 'NODE-----------------')
           
        elif type(entry) == Overlay:
           
            print(hex(entry.address) + '     ' + entry.Id + '     ' + 'OVERLAY')
       
        elif type(entry) == Actor:
           
            print(hex(entry.address) + '     ' + entry.Id + '     ' + 'INSTANCE')
       
        else:
            print("ERROR!!! Unexpected Entry Type in Heap!!!!!!!!!")
 
 
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
 
def Allocate_Fish(Heap, Room_Number, Overlay_dict):
   
    Fish = Actor(name='Fish', Id='0017', size=636, category=0, overlay_type='A', unloadable=True, address=0, room_number=Room_Number, priority=0, from_spawner=False, transition=False, clearable=False, cleared=False)
   
    Allocate(Heap, Fish, Overlay_dict)
 
 
def Allocate_Bugs(Heap, Room_Number, Overlay_dict):
   
    """
   
   This function allocates a set of 3 bugs to the Heap
   
   """
   
    for i in range(3):
        Bug = Actor(name='Bug', Id='017B', size=884, category=0, overlay_type='A', unloadable=True, address=0, room_number=Room_Number, priority=i, from_spawner=False, transition=False, clearable=False, cleared=False)
   
        Allocate(Heap, Bug, Overlay_dict)
 
 
def Allocate_Bomb(Heap, Room_Number, Overlay_dict):
   
    Bomb = Actor(name='Bomb', Id='0009', size=516, category=0, overlay_type='B', unloadable=True, address=0, room_number=Room_Number, priority=0, from_spawner=False, transition=False, clearable=False, cleared=False)
   
    Allocate(Heap, Bomb, Overlay_dict)
 
 
def Allocate_Smoke(Heap, Room_Number, Overlay_dict):
   
    """
   
   This function allocates a bomb, then allocates smoke (this happens when the bomb explodes)
   and then deallocates the bomb (we bothered allocating the bomb to ensure that the smoke
   appears in the right spot in the Heap)
   
   Note that we should never allow ourselves to allocate smoke AFTER calling Allocate_Bomb()
   because in reality the first bomb would explode first (this isn't strictly true, but we should
   do it this way at least in the simple script)
   
   """
   
    Bomb = Actor(name='Bomb', Id='0009', size=516, category=0, overlay_type='B', unloadable=True, address=0, room_number=Room_Number, priority=0, from_spawner=False, transition=False, clearable=False, cleared=False)
   
    Allocate(Heap, Bomb, Overlay_dict)
   
    Smoke = Actor(name='Smoke', Id='00A2', size=11908, category=0, overlay_type='A', unloadable=True, address=0, room_number=Room_Number, priority=0, from_spawner=False, transition=False, clearable=False, cleared=False)
   
    Allocate(Heap, Smoke, Overlay_dict)
   
    Deallocate(Heap, Bomb, Overlay_dict)
 
def Allocate_Arrow(Heap, Room_Number, Overlay_dict):
   
    """
   
   This function allocates an arrow into the heap. Note that Deku Bubbles are
   the same actor as arrows (in that they're both 000F)
   
   """
   
    Arrow = Actor(name='Arrow', Id='000F', size=632, category=0, overlay_type='B', unloadable=True, address=0, room_number=Room_Number, priority=0, from_spawner=False, transition=False, clearable=False, cleared=False)
   
    Allocate(Heap, Arrow, Overlay_dict)
 
 
def Allocate_Hookshot(Heap, Room_Number, Overlay_dict):
   
    Hookshot = Actor(name='Hookshot', Id='003D', size=528, category=0, overlay_type='B', unloadable=True, address=0, room_number=Room_Number, priority=0, from_spawner=False, transition=False, clearable=False, cleared=False)
   
    Allocate(Heap, Hookshot, Overlay_dict)
 
 
def Allocate_Chu(Heap, Room_Number, Overlay_dict):
   
    Chu = Actor(name='Chu', Id='006A', size=480, category=0, overlay_type='B', unloadable=True, address=0, room_number=Room_Number, priority=0, from_spawner=False, transition=False, clearable=False, cleared=False)
   
    Allocate(Heap, Chu, Overlay_dict)
 
 
def Allocate_Zora_Fins(Heap, Room_Number, Overlay_dict):
   
    """
   
   This function allocates 2 Zora Fin actor instances
   
   """
   
    for i in range(2):
       
        Zora_Fin = Actor(name='Zora Fin', Id='0020', size=500, category=0, overlay_type='B', unloadable=True, address=0, room_number=Room_Number, priority=0, from_spawner=False, transition=False, clearable=False, cleared=False)
       
        Allocate(Heap, Zora_Fin, Overlay_dict)
 
 
def Allocate_Charged_Spin_Attack(Heap, Room_Number, Overlay_dict):
   
    """
   
   This functions allocates the Spin Attack & Sword Beam Effects and then the
   Spin Attack Charge Particles (This is the order they get allocated in when
   you charge a spin attack)
   
   """
   
    Spin_Attack_and_Sword_Beam_Effects = Actor(name='Spin Attack & Sword Beam Effects', Id='0035', size=452, category=0, overlay_type='B', unloadable=True, address=0, room_number=Room_Number, priority=0, from_spawner=False, transition=False, clearable=False, cleared=False)
   
    Allocate(Heap, Spin_Attack_and_Sword_Beam_Effects, Overlay_dict)
   
    Spin_Attack_Charge_Particles = Actor(name='Spin Attack Charge Particles', Id='007B', size=1367, category=0, overlay_type='A', unloadable=True, address=0, room_number=Room_Number, priority=0, from_spawner=False, transition=False, clearable=False, cleared=False)
   
    Allocate(Heap, Spin_Attack_Charge_Particles, Overlay_dict)
 
 
 
 
def Allocate_Gold_Skulltula_With_Hookshot(Heap, Room_Number, Overlay_dict):
   
    """
   
   This function allocates a gold skulltula (for example, if you shoot a skull-
   kid painting that reveals a gold skulltula, it allocates a gold skulltula)
   
   It first allocates an hookshot, then the gold skulltula, then deallocates the hookshot
   
   THIS FUNCTION HARDCODES THE PRIORITY OF THE GOLD SKULLTULA TO BE 5 BECAUSE
   I ONLY CARE ABOUT ROOM 3 OF OCEANSIDE SPIDERHOUSE
   
   """
   
    Gold_Skulltula = Actor(name='Gold Skulltula', Id='0050', size=0x4A4, category=5, overlay_type='A', unloadable=True, address=0, room_number=Room_Number, priority=5, from_spawner=False, transition=False, clearable=True, cleared=False)
   
    if Gold_Skulltula.room_number != 3:
        print("ERROR: Gold_Skulltula has room_number != 3 ?????? (Allocate_Gold_Skulltula() Error Message)")
   
   
    Hookshot = Actor(name='Hookshot', Id='003D', size=528, category=0, overlay_type='B', unloadable=True, address=0, room_number=Room_Number, priority=0, from_spawner=False, transition=False, clearable=False, cleared=False)
   
    Allocate(Heap, Hookshot, Overlay_dict)
   
    Allocate(Heap, Gold_Skulltula, Overlay_dict)
   
    Deallocate(Heap, Hookshot, Overlay_dict)
 
 
def Allocate_Gold_Skulltula_With_Arrow(Heap, Room_Number, Overlay_dict):
   
    """
   
   This function allocates a gold skulltula (for example, if you shoot a skull-
   kid painting that reveals a gold skulltula, it allocates a gold skulltula)
   
   It first allocates an arrow, then the gold skulltula, then deallocates the arrow
   
   THIS FUNCTION HARDCODES THE PRIORITY OF THE GOLD SKULLTULA TO BE 5 BECAUSE
   I ONLY CARE ABOUT ROOM 3 OF OCEANSIDE SPIDERHOUSE
   
   """
   
    Gold_Skulltula = Actor(name='Gold Skulltula', Id='0050', size=0x4A4, category=5, overlay_type='A', unloadable=True, address=0, room_number=Room_Number, priority=5, from_spawner=False, transition=False, clearable=True, cleared=False)
   
    if Gold_Skulltula.room_number != 3:
        print("ERROR: Gold_Skulltula has room_number != 3 ?????? (Allocate_Gold_Skulltula() Error Message)")
   
   
    Arrow = Actor(name='Arrow', Id='000F', size=632, category=0, overlay_type='B', unloadable=True, address=0, room_number=Room_Number, priority=0, from_spawner=False, transition=False, clearable=False, cleared=False)
   
    Allocate(Heap, Arrow, Overlay_dict)
   
    Allocate(Heap, Gold_Skulltula, Overlay_dict)
   
    Deallocate(Heap, Arrow, Overlay_dict)
   
 
def Kill_Gold_Skulltula(Heap, Gold_Skulltula, Room_Number, Overlay_dict):
   
    """
   
   TODO: can implement this for more oceanside possibilties
   
   This function kills a gold skulltula to spawn a gold skulltula token
   WITHOUT using something that spawns an actor (like hookshot or an arrow)
   
   
   it matters how you kill it because the token needs to allocate (hookshot, arrow, sword, fins)
   
   """
   
    if Gold_Skulltula.Id != '0050':
        print("ERROR: Gold_Skulltula is not actually a gold skulltula (Kill_Gold_Skulltula() Error Message)")
   
    Gold_Skulltula_Token = Actor(name='Gold Skulltula Token', Id='00E3', size=0x1A0, category=0, overlay_type='A', unloadable=True, address=0, room_number=Room_Number, priority=Gold_Skulltula.priority, from_spawner=False, transition=False, clearable=True, cleared=False)
   
    Allocate(Heap, Gold_Skulltula_Token, Overlay_dict)
   
    Deallocate(Heap, Gold_Skulltula, Overlay_dict)
   
 
def Kill_Gold_Skulltula_With_Hookshot(Heap, Gold_Skulltula, Room_Number, Overlay_dict):
   
    """
   
   TODO: can implement this for more oceanside possibilties
   
   This function kills a gold skulltula to spawn a gold skulltula token with hookshot
   
   
   it matters how you kill it because the token needs to allocate (hookshot, arrow, sword, fins)
   
   """
   
    if Gold_Skulltula.Id != '0050':
        print("ERROR: Gold_Skulltula is not actually a gold skulltula (Kill_Gold_Skulltula_With_Hookshot() Error Message)")
   
    Gold_Skulltula_Token = Actor(name='Gold Skulltula Token', Id='00E3', size=0x1A0, category=0, overlay_type='A', unloadable=True, address=0, room_number=Room_Number, priority=Gold_Skulltula.priority, from_spawner=False, transition=False, clearable=True, cleared=False)
   
    Hookshot = Actor(name='Hookshot', Id='003D', size=528, category=0, overlay_type='B', unloadable=True, address=0, room_number=Room_Number, priority=0, from_spawner=False, transition=False, clearable=False, cleared=False)
   
    Allocate(Heap, Hookshot, Overlay_dict)
   
    Allocate(Heap, Gold_Skulltula_Token, Overlay_dict)
   
    Deallocate(Heap, Gold_Skulltula, Overlay_dict)
   
    Deallocate(Heap, Hookshot, Overlay_dict)
 
 
def Kill_Gold_Skulltula_With_Arrow(Heap, Gold_Skulltula, Room_Number, Overlay_dict):
   
    """
   
   TODO: can implement this for more oceanside possibilties
   
   This function kills a gold skulltula to spawn a gold skulltula token with hookshot
   
   
   it matters how you kill it because the token needs to allocate (hookshot, arrow, sword, fins)
   
   """
   
    if Gold_Skulltula.Id != '0050':
        print("ERROR: Gold_Skulltula is not actually a gold skulltula (Kill_Gold_Skulltula_With_Arrow() Error Message)")
   
    Gold_Skulltula_Token = Actor(name='Gold Skulltula Token', Id='00E3', size=0x1A0, category=0, overlay_type='A', unloadable=True, address=0, room_number=Room_Number, priority=Gold_Skulltula.priority, from_spawner=False, transition=False, clearable=True, cleared=False)
   
    Arrow = Actor(name='Arrow', Id='000F', size=632, category=0, overlay_type='B', unloadable=True, address=0, room_number=Room_Number, priority=0, from_spawner=False, transition=False, clearable=False, cleared=False)
   
    Allocate(Heap, Arrow, Overlay_dict)
   
    Allocate(Heap, Gold_Skulltula_Token, Overlay_dict)
   
    Deallocate(Heap, Gold_Skulltula, Overlay_dict)
   
    Deallocate(Heap, Arrow, Overlay_dict)
 
   
 
"""
 
Before proceeding, we should define all of the transitions we plan on passing through
 
Since "Beneath the Graveyard" is relatively simple and I currently only want to consider
passing through a single plane, I will just define Plane_1 to be the plane shared between
Room0 and Room1
 
This loading plane happens the be the second element in Room0_queue, so I will define it based on that
 
"""
 
Plane_1 = Room0_queue[1]
 
 
Transition_List= [Plane_1]
 
 
"""
 
   Grabbable_dict is a dictionary of the grabbable actors (such as pots) that
   we want to attempt to use for superslide SRM where the keys are the grabbable
   actors and the values are lists with 3-bit strings where each bit means:
       
       100 : Possible to enter Plane with both Bomb and Smoke loaded
       010 : Possible to enter Plane with Smoke loaded, but no Bomb loaded
       001 : Possible to enter Plane with no Smoke loaded
   
   and Transitions, where the transitions are the ones you can superslide through
   
   
   
"""
 
Grabbable_dict = {
        Room0_queue[6] : ['100', Plane_1],
        Room0_queue[7] : ['100', Plane_1],
        Room1_queue[25] : ['110', Plane_1],
        Room1_queue[26] : ['100', Plane_1],
        Room1_queue[27] : ['011', Plane_1]
        }
 
 
"""
 
Below this we can consider a sequence of Room loads and then display the Heap
 
"""
 
 
#Load_Scene(Heap, Room0)
 
 
#Load_Room(Heap, Room1, Plane_1, Overlay_dict)
 
#Load_Room(Heap, Room0, Plane_1, Overlay_dict)
 
#Load_Room(Heap, Room1, Plane_1, Overlay_dict)
 
#Load_Room(Heap, Room0, Plane_1, Overlay_dict)
 
 
#Display_Heap(Heap)
 
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
 
 
def Grabbable_In_Room(room, grabbable_actor_list):
   
    """
   
   This function checks the inputted room to see if it contains a grabbale actor
   that we can use for the superslide for SRM (in theory at least...)
   
   """
   
    grabbable_in_room = False
   
    for actor in room.priority_queue:
       
        if type(actor) == Actor and actor.Id in grabbable_actor_list:
           
            grabbable_in_room = True
   
    return grabbable_in_room
 
 
def Valid_Grabbable_In_Room(room, grabbable_actor_dict):
   
    """
   
   This function checks the inputted room to see if it contains a grabbale actor
   that we can use for the superslide for SRM
   
   """
   
    valid_grabbable_in_room = False
   
    for actor in room.priority_queue:
       
        if actor in grabbable_actor_dict.keys():
           
            valid_grabbable_in_room = True
   
    return valid_grabbable_in_room
 
 
def Chest_In_Room(room):
   
    """
   
   This function checks the inputted room to see if it contains a chest
   
   """
   
    chest_in_room = False
   
    for actor in room.priority_queue:
       
        if type(actor) == Actor and actor.Id == '0006':
           
            chest_in_room = True
   
    return chest_in_room
 
 
def Deku_Guard_In_Room(room):
   
    """
   
   This function checks the inputted room to see if it contains a Deku Guard
   
   """
   
    deku_guard_in_room = False
   
    for actor in room.priority_queue:
       
        if type(actor) == Actor and actor.Id == '017A':
           
            deku_guard_in_room = True
   
    return deku_guard_in_room
 
 
def Transition_List(room):
   
    """
   
   This function takes a room as input and returns a list of all of its transitions
   (i.e. doors/loading planes that lead to other rooms)
   
   """
   
    transition_list = []
   
    for actor in room.priority_queue:
       
        if actor.transition != False:
           
            transition_list.append(actor)
           
    return transition_list
   
 
def Shared_Transitions(room1, room2):
   
    """
   
   This function takes two Rooms as input and returns a list of their shared transitions
   (essentially returns the edges connecting these rooms if we view the rooms are nodes
   in a graph)
   
   """
   
    shared_transitions = []
   
    for transition in Transition_List(room1):
       
        if Is_Shared_Transition(transition, room1.number, room2.number) == True:
           
            shared_transitions.append(transition)
   
    return shared_transitions
 
 
def Shared_Transition_Exists(room1, room2):
   
    """
   
   This function takes two Rooms as input and returns True if they share a transition
   and False otherwise
   
   """
   
    shared_transition_exists = False
   
    for transition in Transition_List(room1):
       
        if Is_Shared_Transition(transition, room1.number, room2.number) == True:
           
            shared_transition_exists = True
   
    return shared_transition_exists
 
 
def Neighbors(room, Room_List):
   
    """
   
   This function takes a room as input along with a list of all potential rooms
   and returns a list of all rooms that share a transition with this room (excluding itself)
   
   """
   
    neighbors = []
   
    for ROOM in Room_List:
       
        if ROOM != room and Shared_Transition_Exists(room, ROOM) == True:
           
            neighbors.append(ROOM)
   
    return neighbors
   
 
def New_Room(room, transition, Room_List):
   
    """
   
   This function takes a room, a transition, and a list of all available rooms
   as input and returns the room that you would be in if you started in room
   and passed through transition
   
   """
   
    if transition not in Transition_List(room):
        print("ERROR: Invalid input into New_Room() function; transition is not in room")
       
    for ROOM in Room_List:
       
        if ROOM != room and (transition.transition[0] == ROOM.number or transition.transition[1] == ROOM.number) and ROOM.number != room.number:
           
            new_room = ROOM
   
    return new_room
 
   
def Current_Room(Room_Load_Permutation, Room_List):
   
    """
   
   Room_Load_Permutation is a list whose first element is the initial room that is started at
   
   All subsequent entries are transitions (Actor class objects with transition != False)
   
   
   Room_List is a list of all available Rooms
   
   
   This function returns what Room you would be in after entering every transition listed in
   the permutation, assuming that you start in the initial room
   
   """
   
    if type(Room_Load_Permutation[0]) != Room:
        print("ERROR: no initial room in permutation (Current_Room() function error message)")
   
    current_room = Room_Load_Permutation[0]
   
    if len(Room_Load_Permutation) > 1:
   
        for transition in Room_Load_Permutation[1:len(Room_Load_Permutation)]:
           
            current_room = New_Room(current_room, transition, Room_List)
   
    return current_room
 
 
def Room_Order_List(Room_Load_Permutation, Room_List):
   
    """
   
   Room_Load_Permutation is a list whose first element is the initial room that is started at
   
   All subsequent entries are transitions (Actor class objects with transition != False)
   
   
   Room_List is a list of all available Rooms
   
   
   This function returns a list of what Room you would be in at each step of
   entering transitions
   
   """
   
    if type(Room_Load_Permutation[0]) != Room:
        print("ERROR: no initial room in permutation (Get_Room_Load_List() function error message)")
   
    room_order_list = []
   
    for i in range(0, len(Room_Load_Permutation)):
       
        current_room = Current_Room(Room_Load_Permutation[0:i+1], Room_List)
       
        room_order_list.append(current_room)
   
    return room_order_list
 
 
def Generate_Room_Load_Permutations(Initial_Room, Room_List, Max_Transition_Count):
   
    """
   
   TODO: Debug this function... try calling: Generate_Room_Load_Permutations(Room0, Room_List, 1)
   
   
   This function seems to run for now, but it is untested for when we have multiple planes
   I will test this once I do Deku Palace input
   
   """
   
    """
   
   This function takes as input the initial room (Initial_Room) that the scene was loaded in
   the list of all Rooms we want to consider visiting (Room_List), and Max_Transition_Count
   which is the maximum number of times we want to allow ourselves to load a new room
   
   This function returns a list of all permutations of ways to enter new rooms after starting
   from the initial room (while limiting the number of room loads we do to be exactly Max_Transition_Count)
   where each permutation is a list in the form [Initial_Room, Transition1, Transition2, Transition3, ..., TransitionX]
   for X = Max_Transition_Count (so to get all permutations for X <= Max_Transition_Count, just
   use a for loop and call this function in each iteration of the foor loop and concatenate the lists)
   
   """
   
    if Max_Transition_Count == 0:
       
        new_permutation_list = [[Initial_Room]]
       
        return new_permutation_list
 
   
    else:
       
        new_permutation_list = []
        permutation_list = Generate_Room_Load_Permutations(Initial_Room, Room_List, Max_Transition_Count - 1)
       
        for permutation in permutation_list:
            for room in Neighbors(Current_Room(permutation, Room_List), Room_List):
                for transition in Shared_Transitions(Current_Room(permutation, Room_List), room):
                    new_permutation = copy(permutation)
                    new_permutation.append(transition)
                    #permutation_list.append(new_permutation)
                    new_permutation_list.append(new_permutation)
                   
        return new_permutation_list
 
 
def Generate_All_Room_Load_Permutations(Initial_Room, Room_List, Max_Transition_Count):
   
    """
   
   This function returns all permutations of ways to load a room starting from the initial room
   where the number of room loads is <= Max_Transition_Count
   
   """
   
    permutation_list = []
   
    for N in range(Max_Transition_Count):
       
        new_permutation_list = Generate_Room_Load_Permutations(Initial_Room, Room_List, N)
        permutation_list = permutation_list + new_permutation_list
   
    return permutation_list
 
 
def Generate_Almost_All_Room_Load_Permutations(Initial_Room, Room_List, Max_Transition_Count):
   
    """
   
   This function returns all permutations of ways to load a room starting from the initial room
   where the number of room loads is <= Max_Transition_Count
   
   this will always output a list with length at least 2, which is why it is different
   from Generate_All_Room_Load_Permutations
   
   """
   
    permutation_list = []
   
    for N in range(1, Max_Transition_Count):
       
        new_permutation_list = Generate_Room_Load_Permutations(Initial_Room, Room_List, N)
        permutation_list = permutation_list + new_permutation_list
   
    return permutation_list
 
 
def Generate_All_Room_Order_Lists(Initial_Room, Room_List, Max_Transition_Count):
   
    """
   
   This function returns all permutations of ways to traverse through rooms, starting
   from the initial room where the number of room loads is <= Max_Transition_Count
   
   The distinction between this and Generate_All_Room_Load_Permutations is that
   this will, instead of listing transitions, list the Room you're currently in
   at each step
   
   """
   
    room_order_permutation_list = []
   
    room_load_permutation_list = Generate_All_Room_Load_Permutations(Initial_Room, Room_List, Max_Transition_Count)
   
   
    iteration_count = 0
    for room_load_permutation in room_load_permutation_list:
       
        print("Generate_All_Room_Order_Lists: %d out of %d" %(iteration_count, len(room_load_permutation_list)))
        iteration_count += 1
       
        room_order_list = Room_Order_List(room_load_permutation, Room_List)
       
        room_order_permutation_list.append(room_order_list)
   
    return room_order_permutation_list
       
 
def Generate_Allocation_Permutations(allocation_list):
   
    """
   
   Whatever, I'm just hardcoding a list of all of the actor names I want to allow
   and then using itertools to make a list of all of the permutations
   
   """
   
    """
   
   TODO: Finish this function, also generalize it in the future
   
   """
   
    """
   
   THIS FUNCTION IS SIMPLIFIED AT THE MOMENT AND COULD BE IMPROVED TO GENERATE
   EVEN MORE POSSIBLE PERMUTATIONS
   
   allocation_list is a list of strings of things to allocate
   
   for example:
       
       allocation_list = [
       'Nothing',
       'Bomb',
       'Smoke',
       'Arrow',
       'Hookshot',
       'Charged Spin Attack',
       'Chu',
       'Zora Fins',
       'Fish',
       'Bugs'
       ]
   
   """
   
    allocation_permutation_list = []
   
   
    for i in range(len(allocation_list) + 1):
       
        print("Generate_Allocation_Permutations: %d out of %d" %(i, len(allocation_list)))
       
       
        Permutations = list(itertools.permutations(allocation_list, i))
       
        allocation_permutation_list = allocation_permutation_list + Permutations
   
    return allocation_permutation_list
 
 
def Clear_Instances(actor_id, room):
   
    """
   
   This function takes an actor_id and room as input and sets actor.cleared = True
   for all actors with actor.id == actor_id in room
   
   Call this before loading the scene or anything if you want some specific
   actor cleared already. For example, I'd call Clear_Instances('015B', Room1)
   to clear all of the bad bats in Beneath the Graveyard
   
   """
   
    for actor in room.priority_queue:
       
        if actor.Id == actor_id and actor.clearable == True:
           
            actor.cleared = True
 
 
def Clear_Instance(actor, room):
   
    """
   
   This function takes a specific actor in a room as input and sets
   actor.cleared = True
   
   """
   
    if actor.clearable == True:
       
        actor.cleared = True
 
 
def Generate_Deallocation_Combinations(room):
   
    """
   ##### Note: we actually get combinations instead of permutations because
   the order in which we deallocate actors doesn't matter
   
   This function returns a list of combinations (stored as tuples of Actors)
   
   
   
   Some things this (or maybe some other) function needs to account for:
       
       if any rupee from a rupee cluster is deallocated in a deallocation step,
       then clear the rupee cluster actor instance (00E8) [note that there is
       at most one rupee cluster instance in every room in the game, so there is
       no need to check which cluster the rupees are associated with]
       
       if all bad bats are deallocated on the same deallocation step, then they
       must all be cleared... actually, stronger: if all Category 5 actors with
       the same Id in a given room are deallocated on the same deallocation step,
       then clear all instances... actually this isn't good enough (need to add
       this into the input I believe or just treat bad bats as a special case)
       
   
   """
   
    deallocation_list = []
   
    for actor in room.priority_queue:
       
        if actor.cleared == False and actor.unloadable == True:
           
            deallocation_list.append(actor)
   
    ##### Now we have a list of all actors in room that we have the option of deallocationg
   
    ##### Now want want to generate a list of permutations
    ########## ACTUALLY, order doesn't matter for deallocation, so all combinations suffices
   
    combination_list = []
   
    for i in range(len(deallocation_list) + 1):
       
        Combinations = list(itertools.combinations(deallocation_list, i))
       
        combination_list = combination_list + Combinations
       
    return combination_list
 
 
 
 
def Build_Room_Deallocation_Combination_Graph(room_order_list):
   
   
    """
   
   This function takes a room_order_list as input (that is, a list in the form
   [initial_room, Room1, Room2, Room3, ..., RoomN] which describes the order we
   visit rooms in (note that Roomi could be equal to Roomj even for i =/= j)) and
   returns a dictionary where the keys are vertices whose values are lists of the
   other vertices that they are connected to. Each vertex represents a deallocation
   combination for the room that it corresponds to.
   
   If the edges are directed, then this can be viewed as a multitree with some
   dummy root vertex and then each generation corresponds to a Room.
   
   """
   
    room_count = 0
   
    #### Encode a dummy root node to make finding paths easier
    graph = {('root', room_count - 1) : []}
   
   
    iteration_count = 0
    ### for all rooms except for the last one
    for room in room_order_list[0:len(room_order_list)-1]:
       
        print("Build_Room_Deallocation_Combination_Graph: %d out of %d" %(iteration_count, len(room_order_list) - 1))
        iteration_count += 1
       
        combination_list = Generate_Deallocation_Combinations(room)
       
        for combination in combination_list:
           
            for key in graph.keys():
               
                ### If the key is from the previous generation, then append every combination to its list
                if key[1] == room_count - 1:
                   
                    graph[key].append(combination)
           
            graph[(combination, room_count)] = []
       
        room_count += 1
           
    return graph
 
 
def Find_Leaves(graph):
   
    """
   
   This function takes a graph (really a dictionary) created by Build_Room_Deallocation_Combination_Graph()
   and returns a list of all of its leaves
   
   """
   
    leaf_list = []
 
    for key in graph:
        # only leaves will point to empty lists
        if graph[key] == []:
            leaf_list.append(key)
   
    return leaf_list
 
 
def Find_All_Paths(graph, start, end, path=[]):
       
        """
       
       This function takes a graph (really a dictionary) and start and end vertices
       as input and returns a list of all paths from start to end
       
       TODO: maybe don't rely on hardcoding what the root's key is and instead write
       a function to find it (though hardcode is prob faster if you don't make mistakes)
       
       I will use this to find all paths from ('root', -1) [note that I am hardcoding
       this instead of just finding a root without any parent] to a given lead, and
       I will do this for all leafs (which I can get by doing Find_Leaves(graph))
       
       """
       
       
        path = path + [start]
        if start == end:
            return [path]
        if not (start in graph):
            return []
        paths = []
        for vertex in graph[start]:
            if vertex not in path:
                newpaths = Find_All_Paths(graph, vertex, end, path)
                for newpath in newpaths:
                    paths.append(newpath)
        return paths
 
 
def Find_All_Deallocation_Combination_Paths(graph):
   
    """
   
   TODO: Note that I hardcode what the key of the root vertex is: ('root', -1)
   
   This returns a list of all (n-1)-permutations of deallocation combinations
   for a given room_order_list (where we assume there are n rooms we travel to
   including the initial room). This gives us the thing we called D1
   
   """
   
    all_deallocation_combination_paths = []
   
    leaf_list = Find_Leaves(graph)
   
    iteration_count = 0
    for leaf in leaf_list:
       
        print("Find_All_Deallocation_Combination_Paths: %d out of %d" %(iteration_count, len(leaf_list)))
        iteration_count += 1
       
        # I hardcode the root key to be ('root', -1)
        path_to_leaf = Find_All_Paths(graph, ('root', -1), leaf)
       
        all_deallocation_combination_paths = all_deallocation_combination_paths + path_to_leaf
       
       
    ##### Since every key is a tuple in the form (combination, number), get rid of number part
    for path in all_deallocation_combination_paths:
        for vertex in path:
            path[path.index(vertex)] = vertex[0]
   
    return all_deallocation_combination_paths
 
 
 
 
def Generate_Action_Permutations(room_order_list, allocation_list):
   
    """
   
   THIS IS THE FUNCTION THAT FINALLY GIVES US ALL OF THE PERMUTATIONS OF THINGS
   TO DO FOR A GIVEN room_order_list and the allocation_list.
   
   
   
   WE WILL RUN THIS FUNCTION ON EVERY PERMUTATION OF ROOM ORDER LISTS USING
   Generate_All_Room_Order_Lists(Initial_Room, Room_List, Max_Transition_Count)
   
   
   ONCE WE DO THAT WE WILL HAVE EVERY SINGLE PERMUTATION THAT WE WANT TO TEST
   
   """
   
    allocation_permutations = Generate_Allocation_Permutations(allocation_list)
   
    ##### Now we want all (n-1)-permutations of allocation permutations
    A1 = list(itertools.permutations(allocation_permutations, len(room_order_list) - 1))
   
    #### deallocation combination graph
    graph = Build_Room_Deallocation_Combination_Graph(room_order_list)
   
    D1 = Find_All_Deallocation_Combination_Paths(graph)
   
    ###########################################################################
   
    # create output list o
    o = []
    for i in range(len(A1)):
       
        print("Generate_Action_Permutations: %d out of %d" %(i, len(A1)))
       
        for j in range(len(D1)):
            for b in range(2**(len(room_order_list) - 1)):
                # create new empty list p
                p = []
                for k in range(len(room_order_list) - 1):
                    p.append(room_order_list[k])
                   
                    if bin(b)[2:].zfill(len(room_order_list)-1) == 1:
                       
                        # add each element of A1[i][k] to p
                        for element in A1[i][k]:
                            p.append(element)
                        # add each element of D1[j][k] to p
                        for element in D1[j][k]:
                            p.append(element)
                           
                    elif bin(b)[2:].zfill(len(room_order_list)-1) == 0:
                       
                        # add each element of D1[j][k] to p
                        for element in D1[j][k]:
                            p.append(element)
                        # add each element of A1[i][k] to p
                        for element in A1[i][k]:
                            p.append(element)
               
                # Add the last room to p
                p.append(room_order_list[len(room_order_list)-1])
                # append p to o
                o = o + p
   
    return o
 
 
 
def Generate_Heap_Permutations(Initial_Room, Room_List, Max_Transition_Count, allocation_list):
   
    """
   
   This function takes the initial room, the Room List, the Maximum Number of Transitions
   that we want to allow, and the allocation list as input and returns every permutation
   for heap manip setups to try (possibilities currently mostly limited by allocation_list)
   
   WE WILL USE THIS FUNCTION IN THE HEAP MANIP SOLVER
   
   """
   
    heap_permutations = []
   
    All_Room_Order_Lists = Generate_All_Room_Order_Lists(Initial_Room, Room_List, Max_Transition_Count)
   
    iteration_count= 0
    for room_order_list in All_Room_Order_Lists:
       
        print("Iteration %d out of %d" %(iteration_count, len(All_Room_Order_Lists)))
       
        action_permutations = Generate_Action_Permutations(room_order_list, allocation_list)
       
        heap_permutations = heap_permutations + action_permutations
       
        iteration_count += 1
   
   
    print("HEAP PERMUTATION GENERATION COMPLETE")
   
    return heap_permutations
       
   
 
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
   
def Actor_Is_In_Heap(Heap, actor):
   
    """
   
   actor is the Actor that we want to check for
   
   This function will return True if this Actor is in the Heap and False otherwise
   
   """
   
    actor_is_in_heap = False
   
    for entry in Heap:
       
        if type(entry) == Actor and entry == actor:
           
            actor_is_in_heap = True
   
    return actor_is_in_heap
 
def Actor_Is_In_Room(room, actor):
       
    """
   
   actor is the Actor that we want to check for
   
   This function will return True if this Actor is in the room and False otherwise
   
   """
   
    actor_is_in_room = False
   
    for entry in room.priority_queue:
       
        if type(entry) == Actor and entry == actor:
           
            actor_is_in_room = True
           
    return actor_is_in_room
 
 
 
def Bomb_And_Smoke_Superslide(Heap, Room_Number, Overlay_dict):
   
    """
   
   This function allocates a bomb, then allocates smoke (this happens when the bomb explodes)
   
   """
   
    Bomb = Actor(name='Bomb', Id='0009', size=516, category=0, overlay_type='B', unloadable=True, address=0, room_number=Room_Number, priority=0, from_spawner=False, transition=False, clearable=False, cleared=False)
   
    Allocate(Heap, Bomb, Overlay_dict)
   
    Smoke = Actor(name='Smoke', Id='00A2', size=11908, category=0, overlay_type='A', unloadable=True, address=0, room_number=Room_Number, priority=0, from_spawner=False, transition=False, clearable=False, cleared=False)
   
    Allocate(Heap, Smoke, Overlay_dict)
   
 
 
 
 
def Copy_Room_List(Room_List):
   
    """
   
   This function takes a list of all Rooms, Room_List, as input
   and returns a list of copies of all of the Rooms in Room_List
   
   """
   
    ##### First we want a list of all shared entries between the Room priority queues
   
    shared_actor_list = []
   
    for room1 in Room_List:
        for room2 in Room_List:
           
            if room2 != room1:
               
                for actor1 in room1.priority_queue:
                    for actor2 in room2.priority_queue:
                        if (actor1 == actor2) and (actor1 not in shared_actor_list):
                           
                            shared_actor_list.append(actor1)
                           
    ##### Now make a list of copies of each entry of the above list
   
    shared_actor_copy_list = []
    for actor in shared_actor_list:
        shared_actor_copy_list.append(copy(actor))
   
    Room_List_Copy = []
   
    for room in Room_List:
       
        priority_queue_copy = []
       
        for actor in room.priority_queue:
           
            if actor not in shared_actor_list:
               
                priority_queue_copy.append(copy(actor))
               
            elif actor in shared_actor_list:
                append_count = 0
                for actor2 in shared_actor_copy_list:
                   
                    # If all attributes of the actor and the copy are the same, then assume they are copies of each other
                    if actor2.name == actor.name and actor2.Id == actor.Id and actor2.size == actor.size and actor2.category == actor.category and actor2.overlay_type == actor.overlay_type and actor2.unloadable == actor.unloadable and actor2.address == actor.address and actor2.room_number == actor.room_number and actor2.priority == actor.priority and actor2.from_spawner == actor.from_spawner and actor2.transition == actor.transition and actor2.clearable == actor.clearable and actor2.cleared == actor.cleared:
                        # append the copy  
                        priority_queue_copy.append(actor2)
                        append_count += 1
                       
                        if append_count > 1:
                            print("ERROR: There were two or more copies of the same Actor in shared_actor_copy_list (Copy_Room_List() error message)")
       
       
        room_copy = Room(number=room.number, priority_queue=priority_queue_copy, clock_exists=room.clock_exists, clock_priority=room.clock_priority)
       
        Room_List_Copy.append(room_copy)
   
    return Room_List_Copy
 
 
 
 
def Main_Actor_Attributes_Match(actor1, actor2):
   
    """
   
   This function returns True is the two Actors taken as input have the same
   values for all of their main attributes and False otherwise
   
   the main attributes do not include things like "address" and such that can
   change as the state updates
   
   """
   
    main_actor_attributes_match = False
   
    if actor1.name == actor2.name and actor1.Id == actor2.Id and actor1.size == actor2.size and actor1.category == actor2.category and actor1.overlay_type == actor2.overlay_type and actor1.unloadable == actor2.unloadable and actor1.room_number is actor2.room_number and actor1.priority is actor2.priority and actor1.from_spawner == actor2.from_spawner and actor1.transition == actor2.transition and actor1.clearable == actor2.clearable:
        main_actor_attributes_match = True
   
    return main_actor_attributes_match
 
 
def Main_Overlay_Attributes_Match(overlay1, overlay2):
   
    main_overlay_attributes_match = False
   
    if overlay1.Id == overlay2.Id and overlay1.size == overlay2.size:
        main_overlay_attributes_match = True
   
    return main_overlay_attributes_match
   
 
def Copy_Overlay_Dict(Overlay_Dict):
   
    overlay_dict_copy = {}
   
    for key in Overlay_Dict:
        overlay_dict_copy[key] = copy(Overlay_Dict[key])
   
    return overlay_dict_copy
       
 
def Copy_Heap(Heap, Room_List_Copy, Overlay_Dict_Copy):
   
    """
   
   This function takes the Heap as input and returns a copy of the Heap where
   every actor copy in the Heap copy is the same class instance as each corresponding
   actor in the room list copy priority queues (same for Overlay_Dict_Copy)
   
   """
   
    Heap_Copy = []
   
    for entry in Heap:
       
        entry_allocated = False
        not_allocated_count = 0
        while entry_allocated is False:
           
            if not_allocated_count > 4:
                print("UHHHHHHHHHHHHHHHHHHHHHHHH (Copy_Heap() Error Message)")
       
            if type(entry) == Node:
               
                Heap_Copy.append(copy(entry))
                entry_allocated = True
               
            elif type(entry) == Overlay:
               
                for key in Overlay_Dict_Copy:
                    if Main_Overlay_Attributes_Match(Overlay_Dict_Copy[key], entry) == True:
                        Heap_Copy.append(Overlay_Dict_Copy[key])
                        entry_allocated = True
           
            elif type(entry) == Actor:
               
                allocated_count = 0
                for room in Room_List_Copy:
                   
                    if entry_allocated == True:
                        break
                   
                    for actor in room.priority_queue:
                       
                        if allocated_count > 1:
                            print("ERROR: tried to allocate multiple copies (Copy_Heap() Error Message)")
                       
                        if Main_Actor_Attributes_Match(entry, actor) == True:
                            Heap_Copy.append(actor)
                            allocated_count += 1
                            entry_allocated = True
                            break
               
                # If it isn't in any of the priority queues, then it must be something you spawned
                if entry_allocated == False:
                    Heap_Copy.append(copy(entry))
                    entry_allocated = True
               
            else:
                print("ERROR: entry in Heap is not an Actor, Node, or Overlay (Copy_Heap() error message)")
           
            not_allocated_count += 1
    return Heap_Copy
 
 
def Copy_Grabbable_Dict(Grabbable_Dict, Room_List_Copy):
   
    """
   
   This function takes the Grabbable_Dict as input and returns a copy of the it where
   each transition in it is a the same Actor class instance copy as the ones used in
   the priority queues of the Rooms in Room_List_Copy
   
   """
   
    grabbable_dict_copy = {}
   
    for pot in Grabbable_Dict:
       
        pot_in_dict = False
 
           
        for room in Room_List_Copy:
            if pot_in_dict == True:
                break
            for actor in room.priority_queue:
                if Main_Actor_Attributes_Match(pot, actor) == True:
                   
                    key = actor
                   
                    for room1 in Room_List_Copy:
                        if pot_in_dict == True:
                            break
                        for actor1 in room1.priority_queue:
                           
                            # Finding the transition
                            if Main_Actor_Attributes_Match(Grabbable_Dict[pot][1], actor1):
                               
                                grabbable_dict_copy[key] = [Grabbable_Dict[pot][0], actor1]
                                pot_in_dict = True
                                   
    return grabbable_dict_copy
   
 
def Find_Actor_Copy(actor, Room_List_Copy):
   
    """
   
   This function takes an Actor as input (actor) and a copy of the list of rooms
   (Room_List_Copy) and returns the copy of the inputted actor that is found in
   the priority queue of a Room in Room_List_Copy
   
   """
   
    actor_copy = None
   
    copy_found = False
    for room in Room_List_Copy:
        if copy_found == True:
            break
        for actor1 in room.priority_queue:
            if Main_Actor_Attributes_Match(actor1, actor):
                actor_copy = actor1
                copy_found = True
                break
   
    return actor_copy
           
 
"""
 
TODO: Make the solver take the initial heap layout as input so that it is easy
to test successive heap manip setups in the future
 
DO NOT FORGET TO CLEAR ALL OF THE BAD BATS IF YOU THINK THAT THAT IS SOMETHING
THAT YOU WANT TO DO!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
 
ALSO IGNORE THAT FUNCTION BELOW, COMPLETELY REWRITE FROM SCRATCH BUT MAYBE READ
IT FIRST TO SEE IF IT REMINDS YOU OF ANY IDEAS YOU HAD
 
"""
 
 
def Randomized_Solver(Initial_Room, Room_List, Max_Transition_Count, allocation_list_dict, Grabbable_Dict, Overlay_Dict, filename, Offset_List, Initial_Heap):
   
    """
   
   This function does not currently account for the possibility that you might need to break
   another pot in order to superslide off of a given pot. While this might not be strictly
   true for the pot we currently use in deku palace, it would be good at add more information
   to Grabbable_Dict to account for this
   
   """
   
    """
   
   Okay, the Initial_Heap argument will not work as I initially intended because of things
   like rupee clusters being cleared, etc. So if I want to test a Heap from an initial Heap
   distribution, then I will have to hardcode it to perform the necessary steps to get to it each time
   
   """
   
    """
   
   filename is the complete name (i.e. including the path) that we want to write to
   
   This function will randomly choose solutions to test (it may have repeats)
   
   Offset_List is a list of offsets that we want to check for. The grabbable object (e.g. a pot)
   will be first when calculating the offset. So if doing chest SRM, we want
   pot - chest = 0x160 or pot - chest = 0x1F0, so we want Offset_List = [0x160, 0x1F0]
   We make this Offset_List by default
   
   Grabbable_dict is a dictionary of the grabbable actors (such as pots) that
   we want to attempt to use for superslide SRM where the keys are the grabbable
   actors and the values are 3-bit strings where each bit means:
       
       100 : Possible to enter Plane with both Bomb and Smoke loaded
       010 : Possible to enter Plane with Smoke loaded, but no Bomb loaded
       001 : Possible to enter Plane with no Smoke loaded
   
   """
   
    angle_solution_count = 0
    position_solution_count = 0
    permutation_count = 0
   
    ### Keep doing this forever (infinite loop so we keep trying new permutations)
    while True:
       
        all_room_load_lists = Generate_Almost_All_Room_Load_Permutations(Initial_Room, Room_List, Max_Transition_Count)
       
        for room_load_list in all_room_load_lists:
           
            if permutation_count%500 == 0:
                print("%d Permutations Tested     %d Angle Solutions     %d Position Solutions" %(permutation_count, angle_solution_count, position_solution_count))
            permutation_count += 1
           
            Heap = copy(Initial_Heap)
           
            ##### Initialize the actor addresses and other attributes each time
       
            for room in Room_List:
               
                for actor in room.priority_queue:
                   
                    actor.address = 0
                    actor.cleared = False
                   
                    ##### Clear all bad bats (optional, but I want to do this for beneath the graveyard)
                    Clear_Instances('015B', room)
            ###################################################################
           
            #####
            ##### Perform seuqence of steps here if you want to initialize your heap to something
            #####
           
            # We will use this to collect things we do in the permutation to help output the solution
            action_list = []
           
            room_count = 0
            # NOTE: the first "transition" is actually not a transition; it is the initial room
            for transition in room_load_list[0:len(room_load_list)-1]:
               
                room = Current_Room(room_load_list[0:room_count + 1], Room_List)
               
                # If this is the Initial_Room AND the Heap is empty, then we want to load the scene
                if (room_count is 0) and (len(Heap) == 2):
                   
                    if room != Initial_Room:
                        print("ERROR: first entry in room_load_list is not Initial_Room (Randomnized_Solver() Error Message)")
                   
                    Load_Scene(Heap, Initial_Room, Overlay_Dict)
                    action_list.append("Load Scene: Room %d" %(Initial_Room.number))
                   
                    ##### NOW WE DO DEALLOCATION/ALLOCATION STEPS AFTER LOADING THE SCENE
                   
                   
                    """
                   
                   Now randomly (with some chosen distribution) choose things to allocate
                   and/or things to deallocate (in your current room). Make it so that
                   you can only choose a specific action once. For example, if allocation_list
                   has ['bomb', 'bomb, 'bomb', 'fish'] in it, then make it so you can only use
                   fish once, but you can use bomb 3 times
                   
                   Somehow try to encode that hookshot/charged spin are mutually exclusive
                   and that if either of them exist then they must be the last action
                   
                   Allow yourself to deallocate things before allocating things even
                   though it might be impossible or slow in some cases
                   
                   """
                   
                    # Do a coinflip to decide between allocating or deallocating first
                    #decision_coin_flip = np.random.uniform(0,1)
                    ##### Deterministically do deallocation step first
                    decision_coin_flip = 0
                   
                    # With probability 1/2, we allocate first and deallocate second
                    # if we allocate first, don't allow 'Charged Spin Attack'
                    if decision_coin_flip > .5:
                       
                        explosive_count = 0
                        droppable_count = 0
                       
                        ##### ALLOCATION
                        for action in allocation_list_dict[room.number]:
                           
                            # whether or not we add an action is based off of this
                            coin_flip = np.random.uniform(0,1)
                           
                            if action == 'Smoke' and coin_flip > .5:
                               
                                Allocate_Smoke(Heap, room.number, Overlay_Dict)
                                action_list.append("Allocate: Smoke")
                               
                            elif action == 'Chu' and coin_flip > .5 and explosive_count < 3:
                               
                                Allocate_Chu(Heap, room.number, Overlay_Dict)
                                action_list.append("Allocate: Chu")
                                explosive_count += 1
                               
                            elif action == 'Arrow' and coin_flip > .5:
                               
                                Allocate_Arrow(Heap, room.number, Overlay_Dict)
                                action_list.append("Allocate: Arrow")
                           
                            elif action == 'Bomb' and coin_flip > .5 and explosive_count < 3:
                               
                                Allocate_Bomb(Heap, room.number, Overlay_Dict)
                                action_list.append("Allocate: Bomb")
                                explosive_count += 1
                               
                            elif action == 'Zora Fins' and coin_flip > .5:
                               
                                Allocate_Zora_Fins(Heap, room.number, Overlay_Dict)
                                action_list.append("Allocate: Zora Fins")
                           
                            elif action == 'Fish' and coin_flip > .5 and droppable_count < 2:
                               
                                Allocate_Fish(Heap, room.number, Overlay_Dict)
                                action_list.append("Allocate: Fish")
                                droppable_count += 1
                               
                            elif action == 'Bugs' and coin_flip > .5 and droppable_count < 2:
                               
                                Allocate_Bugs(Heap, room.number, Overlay_Dict)
                                action_list.append("Allocate: Bugs")
                                droppable_count += 1
                           
                            elif action == 'Hookshot' and coin_flip > .5:
                               
                                Allocate_Hookshot(Heap, room.number, Overlay_Dict)
                                action_list.append("Allocate: Hookshot")
                           
                            elif action == 'Gold Skulltula' and coin_flip > .5:
                               
                                projectile_coin_flip = np.random.uniform(0,1)
                               
                                if projectile_coin_flip > .5:
                                    Allocate_Gold_Skulltula_With_Hookshot(Heap, room.number, Overlay_Dict)
                                    action_list.append("Allocate: Gold Skulltula with Hookshot (hit painting)")
                                   
                                elif projectile_coin_flip <= .5:
                                    Allocate_Gold_Skulltula_With_Arrow(Heap, room.number, Overlay_Dict)
                                    action_list.append("Allocate: Gold Skulltula with Arrow (hit painting)")
                                   
                            ### We don't include 'Charged Spin Attack' in this
                       
                        ##### DEALLOCATION
                        for actor in room.priority_queue:
                           
                            # whether or not we deallocate an actor is based off of this
                            coin_flip = np.random.uniform(0,1)
                           
                            ##### HARDCODE TO NOT ALLOW GOLD SKULLTULA OR SPIDER WEBS DEALLOCATE BECAUSE FASTER FOR 100%
                            if actor.unloadable == True and Actor_Is_In_Heap(Heap, actor) == True and coin_flip > .5 and actor.Id != '0050' and actor.Id != '01F4' and actor.Id != '0125':
                               
                               
                                if actor.Id == '00E8' or actor.name == 'Collectible (Rupee from Rupee Cluster)':
                                   
                                    Deallocate(Heap, actor, Overlay_Dict)
                                    # There is at most one rupee cluster per room, so this is fine to clear it
                                    Clear_Instances('00E8', room)
                                    action_list.append("Deallocate: " + actor.name + " (Priority %d)" %(actor.priority))
                               
                                # THESE PRIORITIES ARE HARDCODED FOR ROOM 3 OF OCEANSIDE!!!!!!!
                                elif actor.Id == '01E7' and (actor.priority == 0 or actor.priority == 1 or actor.priority == 2):
                                   
                                    table_bonk_deallocation_count = 0
                                    for entry in Heap:
                                        if type(entry) == Actor and entry.Id == '01E7' and entry.priority == 0:
                                            Deallocate(Heap, entry, Overlay_Dict)
                                            table_bonk_deallocation_count += 1
                                   
                                    for entry in Heap:
                                        if type(entry) == Actor and entry.Id == '01E7' and entry.priority == 1:
                                            Deallocate(Heap, entry, Overlay_Dict)
                                            table_bonk_deallocation_count += 1
                                           
                                    for entry in Heap:
                                        if type(entry) == Actor and entry.Id == '01E7' and entry.priority == 2:
                                            Deallocate(Heap, entry, Overlay_Dict)
                                            table_bonk_deallocation_count += 1
                                   
                                    if table_bonk_deallocation_count != 3:
                                        print("ERROR: table_bonk_deallocation_count is not 3 (Randomized_Solver() error)")
                                   
                                    action_list.append("Deallocate: " + actor.name + " (Priority 0, 1, and 2) [Bonk Oceanside Table]")
                               
                               
                                # if the actor is clearable AND isn't a bad bat, then clear it when deallocating it if it isn't already cleared
                                elif actor.clearable == True and actor.cleared == False and actor.Id != '015B':
                                   
                                    Deallocate(Heap, actor, Overlay_Dict)
                                    action_list.append("Deallocate: " + actor.name + " (Priority %d)" %(actor.priority))
                                    # CLEAR THE ACTOR
                                    Clear_Instance(actor, room)
                                   
                                else:
                                   
                                    Deallocate(Heap, actor, Overlay_Dict)
                                    action_list.append("Deallocate: " + actor.name + " (Priority %d)" %(actor.priority))
                       
                   
                    # With probability 1/2, we deallocate first and allocate second
                    elif decision_coin_flip <= .5:
                   
                        explosive_count = 0
                        droppable_count = 0
                        hookshot_exists = False
                       
                        ##### DEALLOCATION
                        for actor in room.priority_queue:
                           
                            # whether or not we deallocate an actor is based off of this
                            coin_flip = np.random.uniform(0,1)
                           
                            ##### HARDCODE TO NOT ALLOW GOLD SKULLTULA OR SPIDER WEBS DEALLOCATE BECAUSE FASTER FOR 100%
                            if actor.unloadable == True and Actor_Is_In_Heap(Heap, actor) == True and coin_flip > .5 and actor.Id != '0050' and actor.Id != '01F4' and actor.Id != '0125':
                               
                               
                                if actor.Id == '00E8' or actor.name == 'Collectible (Rupee from Rupee Cluster)':
                                   
                                    Deallocate(Heap, actor, Overlay_Dict)
                                    # There is at most one rupee cluster per room, so this is fine to clear it
                                    Clear_Instances('00E8', room)
                                    action_list.append("Deallocate: " + actor.name + " (Priority %d)" %(actor.priority))
                               
                                # THESE PRIORITIES ARE HARDCODED FOR ROOM 3 OF OCEANSIDE!!!!!!!
                                elif actor.Id == '01E7' and (actor.priority == 0 or actor.priority == 1 or actor.priority == 2):
                                   
                                    table_bonk_deallocation_count = 0
                                    for entry in Heap:
                                        if type(entry) == Actor and entry.Id == '01E7' and entry.priority == 0:
                                            Deallocate(Heap, entry, Overlay_Dict)
                                            table_bonk_deallocation_count += 1
                                   
                                    for entry in Heap:
                                        if type(entry) == Actor and entry.Id == '01E7' and entry.priority == 1:
                                            Deallocate(Heap, entry, Overlay_Dict)
                                            table_bonk_deallocation_count += 1
                                           
                                    for entry in Heap:
                                        if type(entry) == Actor and entry.Id == '01E7' and entry.priority == 2:
                                            Deallocate(Heap, entry, Overlay_Dict)
                                            table_bonk_deallocation_count += 1
                                   
                                    if table_bonk_deallocation_count != 3:
                                        print("ERROR: table_bonk_deallocation_count is not 3 (Randomized_Solver() error)")
                                   
                                    action_list.append("Deallocate: " + actor.name + " (Priority 0, 1, and 2) [Bonk Oceanside Table]")
                               
                               
                                # if the actor is clearable AND isn't a bad bat, then clear it when deallocating it if it isn't already cleared
                                elif actor.clearable == True and actor.cleared == False and actor.Id != '015B':
                                   
                                    Deallocate(Heap, actor, Overlay_Dict)
                                    action_list.append("Deallocate: " + actor.name + " (Priority %d)" %(actor.priority))
                                    # CLEAR THE ACTOR
                                    Clear_Instance(actor, room)
                                   
                                else:
                                   
                                    Deallocate(Heap, actor, Overlay_Dict)
                                    action_list.append("Deallocate: " + actor.name + " (Priority %d)" %(actor.priority))
                       
 
                        ##### ALLOCATION
                        for action in allocation_list_dict[room.number]:
                           
                            # whether or not we add an action is based off of this
                            coin_flip = np.random.uniform(0,1)
                           
                            if action == 'Smoke' and coin_flip > .5:
                               
                                Allocate_Smoke(Heap, room.number, Overlay_Dict)
                                action_list.append("Allocate: Smoke")
                               
                            elif action == 'Chu' and coin_flip > .5 and explosive_count < 3:
                               
                                Allocate_Chu(Heap, room.number, Overlay_Dict)
                                action_list.append("Allocate: Chu")
                                explosive_count += 1
                               
                            elif action == 'Arrow' and coin_flip > .5:
                               
                                Allocate_Arrow(Heap, room.number, Overlay_Dict)
                                action_list.append("Allocate: Arrow")
                           
                            elif action == 'Bomb' and coin_flip > .5 and explosive_count < 3:
                               
                                Allocate_Bomb(Heap, room.number, Overlay_Dict)
                                action_list.append("Allocate: Bomb")
                                explosive_count += 1
                               
                            elif action == 'Zora Fins' and coin_flip > .5:
                               
                                Allocate_Zora_Fins(Heap, room.number, Overlay_Dict)
                                action_list.append("Allocate: Zora Fins")
                           
                            elif action == 'Fish' and coin_flip > .5 and droppable_count < 2:
                               
                                Allocate_Fish(Heap, room.number, Overlay_Dict)
                                action_list.append("Allocate: Fish")
                                droppable_count += 1
                               
                            elif action == 'Bugs' and coin_flip > .5 and droppable_count < 2:
                               
                                Allocate_Bugs(Heap, room.number, Overlay_Dict)
                                action_list.append("Allocate: Bugs")
                                droppable_count += 1
                           
                            elif action == 'Hookshot' and coin_flip > .5:
                               
                                Allocate_Hookshot(Heap, room.number, Overlay_Dict)
                                action_list.append("Allocate: Hookshot")
                                hookshot_exists = True
                               
                            elif action == 'Charged Spin Attack' and (hookshot_exists is False) and coin_flip > .5:
                               
                                Allocate_Charged_Spin_Attack(Heap, room.number, Overlay_Dict)
                                action_list.append("Allocate: Charged Spin Attack")
                               
                            elif action == 'Gold Skulltula' and coin_flip > .5:
                               
                                projectile_coin_flip = np.random.uniform(0,1)
                               
                                if projectile_coin_flip > .5:
                                    Allocate_Gold_Skulltula_With_Hookshot(Heap, room.number, Overlay_Dict)
                                    action_list.append("Allocate: Gold Skulltula with Hookshot (hit painting)")
                                   
                                elif projectile_coin_flip <= .5:
                                    Allocate_Gold_Skulltula_With_Arrow(Heap, room.number, Overlay_Dict)
                                    action_list.append("Allocate: Gold Skulltula with Arrow (hit painting)")
 
                else:
                   
                    Load_Room(Heap, room, transition, Overlay_Dict)
                   
                    action_list.append("Load Room: Room %d" %(room.number) + " with " + transition.name + " %d" %(transition.priority))
                   
                    """
                   
                   Now randomly (with some chosen distribution) choose things to allocate
                   and/or things to deallocate (in your current room). Make it so that
                   you can only choose a specific action once. For example, if allocation_list
                   has ['bomb', 'bomb, 'bomb', 'fish'] in it, then make it so you can only use
                   fish once, but you can use bomb 3 times
                   
                   Somehow try to encode that hookshot/charged spin are mutually exclusive
                   and that if either of them exist then they must be the last action
                   
                   Allow yourself to deallocate things before allocating things even
                   though it might be impossible or slow in some cases
                   
                   """
                   
                    # Do a coinflip to decide between allocating or deallocating first
                    #decision_coin_flip = np.random.uniform(0,1)
                    ##### Deterministically do deallocation step first
                    decision_coin_flip = 0
                   
                    # With probability 1/2, we allocate first and deallocate second
                    # if we allocate first, don't allow 'Charged Spin Attack'
                    if decision_coin_flip > .5:
                       
                        explosive_count = 0
                        droppable_count = 0
                       
                        ##### ALLOCATION
                        for action in allocation_list_dict[room.number]:
                           
                            # whether or not we add an action is based off of this
                            coin_flip = np.random.uniform(0,1)
                           
                            if action == 'Smoke' and coin_flip > .5:
                               
                                Allocate_Smoke(Heap, room.number, Overlay_Dict)
                                action_list.append("Allocate: Smoke")
                               
                            elif action == 'Chu' and coin_flip > .5 and explosive_count < 3:
                               
                                Allocate_Chu(Heap, room.number, Overlay_Dict)
                                action_list.append("Allocate: Chu")
                                explosive_count += 1
                               
                            elif action == 'Arrow' and coin_flip > .5:
                               
                                Allocate_Arrow(Heap, room.number, Overlay_Dict)
                                action_list.append("Allocate: Arrow")
                           
                            elif action == 'Bomb' and coin_flip > .5 and explosive_count < 3:
                               
                                Allocate_Bomb(Heap, room.number, Overlay_Dict)
                                action_list.append("Allocate: Bomb")
                                explosive_count += 1
                               
                            elif action == 'Zora Fins' and coin_flip > .5:
                               
                                Allocate_Zora_Fins(Heap, room.number, Overlay_Dict)
                                action_list.append("Allocate: Zora Fins")
                           
                            elif action == 'Fish' and coin_flip > .5 and droppable_count < 2:
                               
                                Allocate_Fish(Heap, room.number, Overlay_Dict)
                                action_list.append("Allocate: Fish")
                                droppable_count += 1
                               
                            elif action == 'Bugs' and coin_flip > .5 and droppable_count < 2:
                               
                                Allocate_Bugs(Heap, room.number, Overlay_Dict)
                                action_list.append("Allocate: Bugs")
                                droppable_count += 1
                           
                            elif action == 'Hookshot' and coin_flip > .5:
                               
                                Allocate_Hookshot(Heap, room.number, Overlay_Dict)
                                action_list.append("Allocate: Hookshot")
                           
                            elif action == 'Gold Skulltula' and coin_flip > .5:
                               
                                projectile_coin_flip = np.random.uniform(0,1)
                               
                                if projectile_coin_flip > .5:
                                    Allocate_Gold_Skulltula_With_Hookshot(Heap, room.number, Overlay_Dict)
                                    action_list.append("Allocate: Gold Skulltula with Hookshot (hit painting)")
                                   
                                elif projectile_coin_flip <= .5:
                                    Allocate_Gold_Skulltula_With_Arrow(Heap, room.number, Overlay_Dict)
                                    action_list.append("Allocate: Gold Skulltula with Arrow (hit painting)")
                       
                            ### We don't include 'Charged Spin Attack' in this
                       
                        ##### DEALLOCATION
                        for actor in room.priority_queue:
                           
                            # whether or not we deallocate an actor is based off of this
                            coin_flip = np.random.uniform(0,1)
                           
                            ##### HARDCODE TO NOT ALLOW GOLD SKULLTULA OR SPIDER WEBS DEALLOCATE BECAUSE FASTER FOR 100%
                            if actor.unloadable == True and Actor_Is_In_Heap(Heap, actor) == True and coin_flip > .5 and actor.Id != '0050' and actor.Id != '01F4' and actor.Id != '0125':
                               
                               
                                if actor.Id == '00E8' or actor.name == 'Collectible (Rupee from Rupee Cluster)':
                                   
                                    Deallocate(Heap, actor, Overlay_Dict)
                                    # There is at most one rupee cluster per room, so this is fine to clear it
                                    Clear_Instances('00E8', room)
                                    action_list.append("Deallocate: " + actor.name + " (Priority %d)" %(actor.priority))
                               
                                # THESE PRIORITIES ARE HARDCODED FOR ROOM 3 OF OCEANSIDE!!!!!!!
                                elif actor.Id == '01E7' and (actor.priority == 0 or actor.priority == 1 or actor.priority == 2):
                                   
                                    table_bonk_deallocation_count = 0
                                    for entry in Heap:
                                        if type(entry) == Actor and entry.Id == '01E7' and entry.priority == 0:
                                            Deallocate(Heap, entry, Overlay_Dict)
                                            table_bonk_deallocation_count += 1
                                   
                                    for entry in Heap:
                                        if type(entry) == Actor and entry.Id == '01E7' and entry.priority == 1:
                                            Deallocate(Heap, entry, Overlay_Dict)
                                            table_bonk_deallocation_count += 1
                                           
                                    for entry in Heap:
                                        if type(entry) == Actor and entry.Id == '01E7' and entry.priority == 2:
                                            Deallocate(Heap, entry, Overlay_Dict)
                                            table_bonk_deallocation_count += 1
                                   
                                    if table_bonk_deallocation_count != 3:
                                        print("ERROR: table_bonk_deallocation_count is not 3 (Randomized_Solver() error)")
                                   
                                    action_list.append("Deallocate: " + actor.name + " (Priority 0, 1, and 2) [Bonk Oceanside Table]")
                               
                               
                                # if the actor is clearable AND isn't a bad bat, then clear it when deallocating it if it isn't already cleared
                                elif actor.clearable == True and actor.cleared == False and actor.Id != '015B':
                                   
                                    Deallocate(Heap, actor, Overlay_Dict)
                                    action_list.append("Deallocate: " + actor.name + " (Priority %d)" %(actor.priority))
                                    # CLEAR THE ACTOR
                                    Clear_Instance(actor, room)
                                   
                                else:
                                   
                                    Deallocate(Heap, actor, Overlay_Dict)
                                    action_list.append("Deallocate: " + actor.name + " (Priority %d)" %(actor.priority))
                       
                   
                    # With probability 1/2, we deallocate first and allocate second
                    elif decision_coin_flip <= .5:
                   
                        explosive_count = 0
                        droppable_count = 0
                        hookshot_exists = False
                       
                        ##### DEALLOCATION
                        for actor in room.priority_queue:
                           
                            # whether or not we deallocate an actor is based off of this
                            coin_flip = np.random.uniform(0,1)
                           
                            ##### HARDCODE TO NOT ALLOW GOLD SKULLTULA OR SPIDER WEBS DEALLOCATE BECAUSE FASTER FOR 100%
                            if actor.unloadable == True and Actor_Is_In_Heap(Heap, actor) == True and coin_flip > .5 and actor.Id != '0050' and actor.Id != '01F4' and actor.Id != '0125':
                               
                               
                                if actor.Id == '00E8' or actor.name == 'Collectible (Rupee from Rupee Cluster)':
                                   
                                    Deallocate(Heap, actor, Overlay_Dict)
                                    # There is at most one rupee cluster per room, so this is fine to clear it
                                    Clear_Instances('00E8', room)
                                    action_list.append("Deallocate: " + actor.name + " (Priority %d)" %(actor.priority))
                               
                                # THESE PRIORITIES ARE HARDCODED FOR ROOM 3 OF OCEANSIDE!!!!!!!
                                elif actor.Id == '01E7' and (actor.priority == 0 or actor.priority == 1 or actor.priority == 2):
                                   
                                    table_bonk_deallocation_count = 0
                                    for entry in Heap:
                                        if type(entry) == Actor and entry.Id == '01E7' and entry.priority == 0:
                                            Deallocate(Heap, entry, Overlay_Dict)
                                            table_bonk_deallocation_count += 1
                                   
                                    for entry in Heap:
                                        if type(entry) == Actor and entry.Id == '01E7' and entry.priority == 1:
                                            Deallocate(Heap, entry, Overlay_Dict)
                                            table_bonk_deallocation_count += 1
                                           
                                    for entry in Heap:
                                        if type(entry) == Actor and entry.Id == '01E7' and entry.priority == 2:
                                            Deallocate(Heap, entry, Overlay_Dict)
                                            table_bonk_deallocation_count += 1
                                   
                                    if table_bonk_deallocation_count != 3:
                                        print("ERROR: table_bonk_deallocation_count is not 3 (Randomized_Solver() error)")
                                   
                                    action_list.append("Deallocate: " + actor.name + " (Priority 0, 1, and 2) [Bonk Oceanside Table]")
                               
                               
                                # if the actor is clearable AND isn't a bad bat, then clear it when deallocating it if it isn't already cleared
                                elif actor.clearable == True and actor.cleared == False and actor.Id != '015B':
                                   
                                    Deallocate(Heap, actor, Overlay_Dict)
                                    action_list.append("Deallocate: " + actor.name + " (Priority %d)" %(actor.priority))
                                    # CLEAR THE ACTOR
                                    Clear_Instance(actor, room)
                                   
                                else:
                                   
                                    Deallocate(Heap, actor, Overlay_Dict)
                                    action_list.append("Deallocate: " + actor.name + " (Priority %d)" %(actor.priority))
                       
 
                        ##### ALLOCATION
                        for action in allocation_list_dict[room.number]:
                           
                            # whether or not we add an action is based off of this
                            coin_flip = np.random.uniform(0,1)
                           
                            if action == 'Smoke' and coin_flip > .5:
                               
                                Allocate_Smoke(Heap, room.number, Overlay_Dict)
                                action_list.append("Allocate: Smoke")
                               
                            elif action == 'Chu' and coin_flip > .5 and explosive_count < 3:
                               
                                Allocate_Chu(Heap, room.number, Overlay_Dict)
                                action_list.append("Allocate: Chu")
                                explosive_count += 1
                               
                            elif action == 'Arrow' and coin_flip > .5:
                               
                                Allocate_Arrow(Heap, room.number, Overlay_Dict)
                                action_list.append("Allocate: Arrow")
                           
                            elif action == 'Bomb' and coin_flip > .5 and explosive_count < 3:
                               
                                Allocate_Bomb(Heap, room.number, Overlay_Dict)
                                action_list.append("Allocate: Bomb")
                                explosive_count += 1
                               
                            elif action == 'Zora Fins' and coin_flip > .5:
                               
                                Allocate_Zora_Fins(Heap, room.number, Overlay_Dict)
                                action_list.append("Allocate: Zora Fins")
                           
                            elif action == 'Fish' and coin_flip > .5 and droppable_count < 2:
                               
                                Allocate_Fish(Heap, room.number, Overlay_Dict)
                                action_list.append("Allocate: Fish")
                                droppable_count += 1
                               
                            elif action == 'Bugs' and coin_flip > .5 and droppable_count < 2:
                               
                                Allocate_Bugs(Heap, room.number, Overlay_Dict)
                                action_list.append("Allocate: Bugs")
                                droppable_count += 1
                           
                            elif action == 'Hookshot' and coin_flip > .5:
                               
                                Allocate_Hookshot(Heap, room.number, Overlay_Dict)
                                action_list.append("Allocate: Hookshot")
                                hookshot_exists = True
                               
                            elif action == 'Charged Spin Attack' and (hookshot_exists is False) and coin_flip > .5:
                               
                                Allocate_Charged_Spin_Attack(Heap, room.number, Overlay_Dict)
                                action_list.append("Allocate: Charged Spin Attack")
                           
                            elif action == 'Gold Skulltula' and coin_flip > .5:
                               
                                projectile_coin_flip = np.random.uniform(0,1)
                               
                                if projectile_coin_flip > .5:
                                    Allocate_Gold_Skulltula_With_Hookshot(Heap, room.number, Overlay_Dict)
                                    action_list.append("Allocate: Gold Skulltula with Hookshot (hit painting)")
                                   
                                elif projectile_coin_flip <= .5:
                                    Allocate_Gold_Skulltula_With_Arrow(Heap, room.number, Overlay_Dict)
                                    action_list.append("Allocate: Gold Skulltula with Arrow (hit painting)")
                   
                room_count += 1
           
            ##### Now we load the last room in room_order_list
            current_room = Current_Room(room_load_list, Room_List)
            most_recent_transition = room_load_list[-1]
            Load_Room(Heap, current_room, most_recent_transition, Overlay_Dict)
           
            action_list.append("Load Room: Room %d" %(current_room.number) + " with " + most_recent_transition.name + " %d" %(most_recent_transition.priority))
           
           
            """
           
           Now that we have iterated through all of the rooms, we want to check to see
           if we are in a room with a valid grabbale object. If so, then store the addresses
           of all of them and make a copy of the current Heap state. From here, we want to try
           every possibility in the sense that we want to check every valid grabbable object
           in every room that we can get to and also check every superslide case that is possible
           (based on the binary number associated with each valid grabbable object) and then
           check if either the Angle or Position (input this into the function via Offset_List)
           line up with the chest or deku guard
           
           There aren't too many possibilities from here in practice, so we might as well check them all
           
           Also encode that if we superslide into a room with a chest/deku guard, then we must
           exit the room and then reenter it (or enter another room with a chest/deku guard; we will
           test every case) and after doing that we will check the chest/deku guard addresses
           and see if any of them line up with any of the pots that we stored the addresses of
           
           We'll eventually want to write stuff to a text file, so maybe set file as an input argument
           or just hardcode it, not sure
           
           """
           
            """
           
           WE MAKE THE ASSUMPTION THAT YOU LAND IN A ROOM THAT EITHER IS A ROOM
           WITH A CHEST/DEKU GUARD OR A ROOM THAT NEIGHBORS A ROOM WITH A CHEST/DEKU GUARD
           BECAUSE I CANNOT THINK OF ANY PLACES WHERE THIS WOULDN'T HAPPEN WHEN TESTING
           SUPERSLIDE SRM (ZORA FIN WOULD BE DIFFERENT, BUT THIS SOLVER DOESN'T TEST IT)
           
           Also, before supersliding, we assume that you're in a room that either has
           a valid grabbable object, or is next to a room with a valid grabbable object.
           Of course, this means fewer possibilities are being tested in a place like
           oceanside, but there are already so many possibilities to test to begin with that
           this probably isn't a big deal for now. This also affects deku palace, but maybe
           I'll change this by the time I work on deku palace (because if you end in Room2,
           then nothing happens)
           
           """
           
            """
           
           Nevermind some of those other comments, here is what I'm really assuming.
           
           I will be assuming that if you end in a room without a valid grabbable
           actor, then it will search all neighbors of that room for valid grabbable
           actors and if none of those have valid grabbable objects then it will
           search all of those neighbors and choose the first one it finds (this
           will allow for ending in Room 2 in Deku Palace). Otherwise it does nothing
           (though this will never happen for the cases I plan on checking for now)
           
           (*Coded)If you are in a room with a valid grabbable actor and no chest/deku guard,
           then we will check the addresses of all valid grabbable actors in this room
           and superslide into the chest room, exit and reenter it. Then we will check the address of the
           chest and see if it lines up with any of the pot addresses from the previous
           room.
           
           (*Coded)If you are in a room with a valid grabbable actor AND a chest/deku guard, then
           you will record the valid grabbable actor addresses then superslide to exit the
           room and then check all neighbors of the room you enter for having a chest/deku guard
           and test all of them
           
           
           
           """
           
            valid_grabbable_actor_room_list = []
           
            for room in Room_List:
                if Valid_Grabbable_In_Room(room, Grabbable_Dict) is True:
                    valid_grabbable_actor_room_list.append(room)
           
            # This gives a list of all ways we can exit our current room
            #transition_list_possibilities = Generate_Room_Load_Permutations(current_room, Room_List, 1)
           
            ##### Case 1: there is a valid grabbable actor in the current room, but no chest/deku guard (the guard thing doesn't matter because this never happens in palace anyway)
            if (current_room in valid_grabbable_actor_room_list) and (Chest_In_Room(current_room) is False) and (Deku_Guard_In_Room(current_room) is False):
               
                valid_pot_list = []
                pot_address_list = []
               
                for pot in Grabbable_Dict:
                   
                    if Actor_Is_In_Room(current_room, pot) is True:
                        valid_pot_list.append(pot)
                        pot_address_list.append(pot.address)
               
                """
               
               Now for each pot in valid_pot_list, we want to test every applicable
               superslide scenario
               
               Before each one, we need to copy the current state and then modify the copies
               to check for the solution
               
               """
               
                for pot in valid_pot_list:
                   
                    # both bomb and smoke loaded on superslide
                    if Grabbable_Dict[pot][0][0] == '1':
                       
                        action_list100 = []
                       
                        # COPY STATE
                        #######################################################
                        Room_List_Copy = Copy_Room_List(Room_List)
                        Overlay_Dict_Copy = Copy_Overlay_Dict(Overlay_Dict)
                       
                        room_copy_dict = {}
                        for room in Room_List_Copy:
                            room_copy_dict[room.number] = room
                       
                        Heap_Copy = Copy_Heap(Heap, Room_List_Copy, Overlay_Dict_Copy)
                       
                        Grabbable_Dict_Copy = Copy_Grabbable_Dict(Grabbable_Dict, Room_List_Copy)
                        #######################################################
                       
                        Bomb_And_Smoke_Superslide(Heap_Copy, current_room.number, Overlay_Dict_Copy)
                        action_list100.append("Superslide with Bomb and Smoke still allocated")
                       
                        # The room we superslide into through the plane corresponding to the given pot
                        destination_room = Current_Room([current_room, Grabbable_Dict[pot][1]], Room_List)
                       
                        destination_room_copy = room_copy_dict[destination_room.number]
                        current_room_copy = room_copy_dict[current_room.number]
                       
                        pot_copy = Find_Actor_Copy(pot, Room_List_Copy)
                        superslide_transition_copy = Grabbable_Dict_Copy[pot_copy][1]
                       
                        Load_Room(Heap_Copy, destination_room_copy, superslide_transition_copy, Overlay_Dict_Copy)
                        action_list100.append("Load Room: Room %d" %(destination_room_copy.number) + " with " + superslide_transition_copy.name + " %d" %(superslide_transition_copy.priority))
                       
                        # Now exit the chest room
                        Load_Room(Heap_Copy, current_room_copy, superslide_transition_copy, Overlay_Dict_Copy)
                        action_list100.append("Load Room: Room %d" %(current_room_copy.number) + " with " + superslide_transition_copy.name + " %d" %(superslide_transition_copy.priority))
                       
                        # Now reenter the chest room
                        Load_Room(Heap_Copy, destination_room_copy, superslide_transition_copy, Overlay_Dict_Copy)
                        action_list100.append("Load Room: Room %d" %(destination_room_copy.number) + " with " + superslide_transition_copy.name + " %d" %(superslide_transition_copy.priority))
                       
                        ##### Now check for chests/deku guards
                       
                        chest_guard_list = []
                       
                        for entry in Heap_Copy:
                           
                            if type(entry) == Actor and (entry.Id == '0006' or entry.Id == '017A'):
                                chest_guard_list.append(entry)
                       
                        soln_found = False
                        for entry in chest_guard_list:
                            if (pot.address - entry.address) in Offset_List:
                               
                                action_list100.append("SOLUTION: " + pot.name + " (Priority %d)" %(pot.priority) + " from Room %d" %(pot.room_number) + " lines up with " + entry.name + " (Priority %d)" %(entry.priority) + " from Room %d" %(entry.room_number) + " with offset: " + hex(pot.address - entry.address))
                               
                                if (pot.address - entry.address) == 0x160:
                                    angle_solution_count += 1
                                    print("ANGLE SOLUTION FOUND (CHEST)!!!!!!!!!!!")
                                elif (pot.address - entry.address) == 0x1F0:
                                    position_solution_count += 1
                                    print("Z POSITION SOLUTION FOUND (CHEST)!!!!!!!!!!!")
                               
                                soln_found = True
                               
                        if soln_found is True:
                            total_action_list = action_list + action_list100
                           
                            # the "a" argument is important so we don't overwrite previous solutions
                            with open(filename, "a") as file:
                               
                                for action in total_action_list:
                                   
                                    file.write(action + "\n")
                                file.write("-----\n")
                   
                   
                    ##### Only smoke is loaded from superslide
                    elif Grabbable_Dict[pot][0][1] == '1':
                       
                        action_list010 = []
                       
                        # COPY STATE
                        #######################################################
                        Room_List_Copy = Copy_Room_List(Room_List)
                        Overlay_Dict_Copy = Copy_Overlay_Dict(Overlay_Dict)
                       
                        room_copy_dict = {}
                        for room in Room_List_Copy:
                            room_copy_dict[room.number] = room
                       
                        Heap_Copy = Copy_Heap(Heap, Room_List_Copy, Overlay_Dict_Copy)
                       
                        Grabbable_Dict_Copy = Copy_Grabbable_Dict(Grabbable_Dict, Room_List_Copy)
                        #######################################################
                       
                        Allocate_Smoke(Heap_Copy, current_room.number, Overlay_Dict_Copy)
                        action_list010.append("Superslide with Smoke still allocated")
                       
                        # The room we superslide into through the plane corresponding to the given pot
                        destination_room = Current_Room([current_room, Grabbable_Dict[pot][1]], Room_List)
                       
                        destination_room_copy = room_copy_dict[destination_room.number]
                        current_room_copy = room_copy_dict[current_room.number]
                       
                        pot_copy = Find_Actor_Copy(pot, Room_List_Copy)
                        superslide_transition_copy = Grabbable_Dict_Copy[pot_copy][1]
                       
                        Load_Room(Heap_Copy, destination_room_copy, superslide_transition_copy, Overlay_Dict_Copy)
                        action_list010.append("Load Room: Room %d" %(destination_room_copy.number) + " with " + superslide_transition_copy.name + " %d" %(superslide_transition_copy.priority))
                       
                        # Now exit the chest room
                        Load_Room(Heap_Copy, current_room_copy, superslide_transition_copy, Overlay_Dict_Copy)
                        action_list010.append("Load Room: Room %d" %(current_room_copy.number) + " with " + superslide_transition_copy.name + " %d" %(superslide_transition_copy.priority))
                       
                        # Now reenter the chest room
                        Load_Room(Heap_Copy, destination_room_copy, superslide_transition_copy, Overlay_Dict_Copy)
                        action_list010.append("Load Room: Room %d" %(destination_room_copy.number) + " with " + superslide_transition_copy.name + " %d" %(superslide_transition_copy.priority))
                       
                       
                        ##### Now check for chests/deku guards
                       
                        chest_guard_list = []
                       
                        for entry in Heap_Copy:
                           
                            if type(entry) == Actor and (entry.Id == '0006' or entry.Id == '017A'):
                                chest_guard_list.append(entry)
                       
                        soln_found = False
                        for entry in chest_guard_list:
                            if (pot.address - entry.address) in Offset_List:
                               
                                action_list010.append("SOLUTION: " + pot.name + " (Priority %d)" %(pot.priority) + " from Room %d" %(pot.room_number) + " lines up with " + entry.name + " (Priority %d)" %(entry.priority) + " from Room %d" %(entry.room_number) + " with offset: " + hex(pot.address - entry.address))
                               
                                if (pot.address - entry.address) == 0x160:
                                    angle_solution_count += 1
                                    print("ANGLE SOLUTION FOUND (CHEST)!!!!!!!!!!!")
                                elif (pot.address - entry.address) == 0x1F0:
                                    position_solution_count += 1
                                    print("Z POSITION SOLUTION FOUND (CHEST)!!!!!!!!!!!")
                               
                                soln_found = True
                               
                        if soln_found is True:
                            total_action_list = action_list + action_list010
                           
                            # the "a" argument is important so we don't overwrite previous solutions
                            with open(filename, "a") as file:
                               
                                for action in total_action_list:
                                   
                                    file.write(action + "\n")
                                file.write("-----\n")
                   
                   
                    #### Bomb and Smoke are both unloaded
                    elif Grabbable_Dict[pot][0][2] == '1':
                       
                        action_list001 = []
                       
                        # COPY STATE
                        #######################################################
                        Room_List_Copy = Copy_Room_List(Room_List)
                        Overlay_Dict_Copy = Copy_Overlay_Dict(Overlay_Dict)
                       
                        room_copy_dict = {}
                        for room in Room_List_Copy:
                            room_copy_dict[room.number] = room
                       
                        Heap_Copy = Copy_Heap(Heap, Room_List_Copy, Overlay_Dict_Copy)
                       
                        Grabbable_Dict_Copy = Copy_Grabbable_Dict(Grabbable_Dict, Room_List_Copy)
                        #######################################################
                       
                        # Do not allocate anything
                        action_list001.append("Superslide with Bomb and Smoke unloaded when passing plane")
                       
                        # The room we superslide into through the plane corresponding to the given pot
                        destination_room = Current_Room([current_room, Grabbable_Dict[pot][1]], Room_List)
                       
                        destination_room_copy = room_copy_dict[destination_room.number]
                        current_room_copy = room_copy_dict[current_room.number]
                       
                        pot_copy = Find_Actor_Copy(pot, Room_List_Copy)
                        superslide_transition_copy = Grabbable_Dict_Copy[pot_copy][1]
                       
                        Load_Room(Heap_Copy, destination_room_copy, superslide_transition_copy, Overlay_Dict_Copy)
                        action_list001.append("Load Room: Room %d" %(destination_room_copy.number) + " with " + superslide_transition_copy.name + " %d" %(superslide_transition_copy.priority))
                       
                        # Now exit the chest room
                        Load_Room(Heap_Copy, current_room_copy, superslide_transition_copy, Overlay_Dict_Copy)
                        action_list001.append("Load Room: Room %d" %(current_room_copy.number) + " with " + superslide_transition_copy.name + " %d" %(superslide_transition_copy.priority))
                       
                        # Now reenter the chest room
                        Load_Room(Heap_Copy, destination_room_copy, superslide_transition_copy, Overlay_Dict_Copy)
                        action_list001.append("Load Room: Room %d" %(destination_room_copy.number) + " with " + superslide_transition_copy.name + " %d" %(superslide_transition_copy.priority))
                       
                       
                        ##### Now check for chests/deku guards
                       
                        chest_guard_list = []
                       
                        for entry in Heap_Copy:
                           
                            if type(entry) == Actor and (entry.Id == '0006' or entry.Id == '017A'):
                                chest_guard_list.append(entry)
                       
                        soln_found = False
                        for entry in chest_guard_list:
                            if (pot.address - entry.address) in Offset_List:
                               
                                action_list001.append("SOLUTION: " + pot.name + " (Priority %d)" %(pot.priority) + " from Room %d" %(pot.room_number) + " lines up with " + entry.name + " (Priority %d)" %(entry.priority) + " from Room %d" %(entry.room_number) + " with offset: " + hex(pot.address - entry.address))
                               
                                if (pot.address - entry.address) == 0x160:
                                    angle_solution_count += 1
                                    print("ANGLE SOLUTION FOUND (CHEST)!!!!!!!!!!!")
                                elif (pot.address - entry.address) == 0x1F0:
                                    position_solution_count += 1
                                    print("Z POSITION SOLUTION FOUND (CHEST)!!!!!!!!!!!")
                               
                                soln_found = True
                               
                        if soln_found is True:
                            total_action_list = action_list + action_list001
                           
                            # the "a" argument is important so we don't overwrite previous solutions
                            with open(filename, "a") as file:
                               
                                for action in total_action_list:
                                   
                                    file.write(action + "\n")
                                file.write("-----\n")
                               
                               
                               
            # Case 2: there is a valid grabbable actor in the current room AND there is a chest or deku guard                  
            elif (current_room in valid_grabbable_actor_room_list) and ((Chest_In_Room(current_room) is True) or (Deku_Guard_In_Room(current_room) is True)):      
               
                valid_pot_list = []
                pot_address_list = []
               
                for pot in Grabbable_Dict:
                   
                    if Actor_Is_In_Room(current_room, pot) is True:
                        valid_pot_list.append(pot)
                        pot_address_list.append(pot.address)
               
               
                """
               
               Now for each pot in valid_pot_list, we want to test every applicable
               superslide scenario
               
               Before each one, we need to copy the current state and then modify the copies
               to check for the solution
               
               Also, for every case, we need to consider every possible room that contains
               a chest/deku guard that neighbors the room we just entered (meaning you
               will need to make copies of the copies of the state)
               
               """
               
                for pot in valid_pot_list:
                   
                    # both bomb and smoke loaded on superslide
                    if Grabbable_Dict[pot][0][0] == '1':
                       
                        action_list100 = []
                       
                        # COPY STATE
                        #######################################################
                        Room_List_Copy = Copy_Room_List(Room_List)
                        Overlay_Dict_Copy = Copy_Overlay_Dict(Overlay_Dict)
                       
                        room_copy_dict = {}
                        for room in Room_List_Copy:
                            room_copy_dict[room.number] = room
                       
                        Heap_Copy = Copy_Heap(Heap, Room_List_Copy, Overlay_Dict_Copy)
                       
                        Grabbable_Dict_Copy = Copy_Grabbable_Dict(Grabbable_Dict, Room_List_Copy)
                        #######################################################
                       
                        Bomb_And_Smoke_Superslide(Heap_Copy, current_room.number, Overlay_Dict_Copy)
                        action_list100.append("Superslide with Bomb and Smoke still allocated")
                       
                        # The room we superslide into through the plane corresponding to the given pot
                        destination_room = Current_Room([current_room, Grabbable_Dict[pot][1]], Room_List)
                       
                        destination_room_copy = room_copy_dict[destination_room.number]
                       
                        pot_copy = Find_Actor_Copy(pot, Room_List_Copy)
                        superslide_transition_copy = Grabbable_Dict_Copy[pot_copy][1]
                       
                        Load_Room(Heap_Copy, destination_room_copy, superslide_transition_copy, Overlay_Dict_Copy)
                        action_list100.append("Load Room: Room %d" %(destination_room_copy.number) + " with " + superslide_transition_copy.name + " %d" %(superslide_transition_copy.priority))
                       
                        """
                       
                       Now we check all neighbors of our current room (destination_room) and for
                       each neighbor that has a chest or deku guard in it, we will create a copy
                       of our copy of the state, then enter each of them through each possible
                       loading plane and then check the chest/guard addresses and see if anything
                       lines up
                       
                       """
                       
                        for neighbor in Neighbors(destination_room, Room_List):
                           
                            if Chest_In_Room(neighbor) == True or Deku_Guard_In_Room(neighbor) == True:
                               
                                for transition in Shared_Transitions(destination_room, neighbor):
                                   
                                     # COPY STATE
                                    #######################################################
                                    Room_List_Copy_2 = Copy_Room_List(Room_List_Copy)
                                    Overlay_Dict_Copy_2 = Copy_Overlay_Dict(Overlay_Dict_Copy)
                                   
                                    room_copy_dict_2 = {}
                                    for room in Room_List_Copy_2:
                                        room_copy_dict_2[room.number] = room
                                   
                                    Heap_Copy_2 = Copy_Heap(Heap_Copy, Room_List_Copy_2, Overlay_Dict_Copy_2)
                                   
                                    Grabbable_Dict_Copy_2 = Copy_Grabbable_Dict(Grabbable_Dict_Copy, Room_List_Copy_2)
                                    #######################################################
                                   
                                    action_list_2 = []
                                   
                                    transition_copy = Find_Actor_Copy(transition, Room_List_Copy_2)
                                   
                                    neighbor_copy = room_copy_dict_2[neighbor.number]
                                   
                                    Load_Room(Heap_Copy_2, neighbor_copy, transition_copy, Overlay_Dict_Copy_2)
                                    action_list_2.append("Load Room: Room %d" %(neighbor_copy.number) + " with " + transition_copy.name + " %d" %(transition_copy.priority))
                                   
                                   
                                    ##### Now check for chests/deku guards
                       
                                    chest_guard_list = []
                                   
                                    for entry in Heap_Copy_2:
                                       
                                        if type(entry) == Actor and (entry.Id == '0006' or entry.Id == '017A'):
                                            chest_guard_list.append(entry)
                                   
                                    soln_found = False
                                    for entry in chest_guard_list:
                                        if (pot.address - entry.address) in Offset_List:
                                           
                                            action_list_2.append("SOLUTION: " + pot.name + " (Priority %d)" %(pot.priority) + " from Room %d" %(pot.room_number) + " lines up with " + entry.name + " (Priority %d)" %(entry.priority) + " from Room %d" %(entry.room_number) + " with offset: " + hex(pot.address - entry.address))
 
                                            if (pot.address - entry.address) == 0x160:
                                                angle_solution_count += 1
                                                print("ANGLE SOLUTION FOUND (CHEST)!!!!!!!!!!!")
                                            elif (pot.address - entry.address) == 0x1F0:
                                                position_solution_count += 1
                                                print("Z POSITION SOLUTION FOUND (CHEST)!!!!!!!!!!!")
 
                                            soln_found = True
                                           
                                    if soln_found is True:
                                        total_action_list = action_list + action_list100 + action_list_2
                                       
                                        # the "a" argument is important so we don't overwrite previous solutions
                                        with open(filename, "a") as file:
                                           
                                            for action in total_action_list:
                                               
                                                file.write(action + "\n")
                                            file.write("-----\n")
                   
                   
                    ##### Only smoke is loaded from superslide
                    elif Grabbable_Dict[pot][0][1] == '1':
                       
                        action_list010 = []
                       
                        # COPY STATE
                        #######################################################
                        Room_List_Copy = Copy_Room_List(Room_List)
                        Overlay_Dict_Copy = Copy_Overlay_Dict(Overlay_Dict)
                       
                        room_copy_dict = {}
                        for room in Room_List_Copy:
                            room_copy_dict[room.number] = room
                       
                        Heap_Copy = Copy_Heap(Heap, Room_List_Copy, Overlay_Dict_Copy)
                       
                        Grabbable_Dict_Copy = Copy_Grabbable_Dict(Grabbable_Dict, Room_List_Copy)
                        #######################################################
                       
                        Allocate_Smoke(Heap_Copy, current_room.number, Overlay_Dict_Copy)
                        action_list010.append("Superslide with Smoke still allocated")
                       
                        # The room we superslide into through the plane corresponding to the given pot
                        destination_room = Current_Room([current_room, Grabbable_Dict[pot][1]], Room_List)
                       
                        destination_room_copy = room_copy_dict[destination_room.number]
                       
                        pot_copy = Find_Actor_Copy(pot, Room_List_Copy)
                        superslide_transition_copy = Grabbable_Dict_Copy[pot_copy][1]
                       
                        Load_Room(Heap_Copy, destination_room_copy, superslide_transition_copy, Overlay_Dict_Copy)
                        action_list010.append("Load Room: Room %d" %(destination_room_copy.number) + " with " + superslide_transition_copy.name + " %d" %(superslide_transition_copy.priority))
                       
                        """
                       
                       Now we check all neighbors of our current room (destination_room) and for
                       each neighbor that has a chest or deku guard in it, we will create a copy
                       of our copy of the state, then enter each of them through each possible
                       loading plane and then check the chest/guard addresses and see if anything
                       lines up
                       
                       """
                       
                        for neighbor in Neighbors(destination_room, Room_List):
                           
                            if Chest_In_Room(neighbor) == True or Deku_Guard_In_Room(neighbor) == True:
 
                                for transition in Shared_Transitions(destination_room, neighbor):
                                   
                                    # COPY STATE
                                    #######################################################
                                    Room_List_Copy_2 = Copy_Room_List(Room_List_Copy)
                                    Overlay_Dict_Copy_2 = Copy_Overlay_Dict(Overlay_Dict_Copy)
                                   
                                    room_copy_dict_2 = {}
                                    for room in Room_List_Copy_2:
                                        room_copy_dict_2[room.number] = room
                                   
                                    Heap_Copy_2 = Copy_Heap(Heap_Copy, Room_List_Copy_2, Overlay_Dict_Copy_2)
                                   
                                    Grabbable_Dict_Copy_2 = Copy_Grabbable_Dict(Grabbable_Dict_Copy, Room_List_Copy_2)
                                    #######################################################
                                   
                                    action_list_2 = []
                                   
                                    transition_copy = Find_Actor_Copy(transition, Room_List_Copy_2)
                                   
                                    neighbor_copy = room_copy_dict_2[neighbor.number]
                                   
                                    Load_Room(Heap_Copy_2, neighbor_copy, transition_copy, Overlay_Dict_Copy_2)
                                    action_list_2.append("Load Room: Room %d" %(neighbor_copy.number) + " with " + transition_copy.name + " %d" %(transition_copy.priority))
                                   
                                   
                                    ##### Now check for chests/deku guards
                       
                                    chest_guard_list = []
                                   
                                    for entry in Heap_Copy_2:
                                       
                                        if type(entry) == Actor and (entry.Id == '0006' or entry.Id == '017A'):
                                            chest_guard_list.append(entry)
                                   
                                    soln_found = False
                                    for entry in chest_guard_list:
                                        if (pot.address - entry.address) in Offset_List:
                                           
                                            action_list_2.append("SOLUTION: " + pot.name + " (Priority %d)" %(pot.priority) + " from Room %d" %(pot.room_number) + " lines up with " + entry.name + " (Priority %d)" %(entry.priority) + " from Room %d" %(entry.room_number) + " with offset: " + hex(pot.address - entry.address))
 
                                            if (pot.address - entry.address) == 0x160:
                                                angle_solution_count += 1
                                                print("ANGLE SOLUTION FOUND (CHEST)!!!!!!!!!!!")
                                            elif (pot.address - entry.address) == 0x1F0:
                                                position_solution_count += 1
                                                print("Z POSITION SOLUTION FOUND (CHEST)!!!!!!!!!!!")
 
                                            soln_found = True
                                           
                                    if soln_found is True:
                                        total_action_list = action_list + action_list010 + action_list_2
                                       
                                        # the "a" argument is important so we don't overwrite previous solutions
                                        with open(filename, "a") as file:
                                           
                                            for action in total_action_list:
                                               
                                                file.write(action + "\n")
                                            file.write("-----\n")
                       
                       
                    #### Bomb and Smoke are both unloaded
                    elif Grabbable_Dict[pot][0][2] == '1':
                       
                        action_list001 = []
                       
                        # COPY STATE
                        #######################################################
                        Room_List_Copy = Copy_Room_List(Room_List)
                        Overlay_Dict_Copy = Copy_Overlay_Dict(Overlay_Dict)
                       
                        room_copy_dict = {}
                        for room in Room_List_Copy:
                            room_copy_dict[room.number] = room
                       
                        Heap_Copy = Copy_Heap(Heap, Room_List_Copy, Overlay_Dict_Copy)
                       
                        Grabbable_Dict_Copy = Copy_Grabbable_Dict(Grabbable_Dict, Room_List_Copy)
                        #######################################################
                       
                        # Do not allocate anything
                        action_list001.append("Superslide with Bomb and Smoke unloaded when passing plane")
                       
                        # The room we superslide into through the plane corresponding to the given pot
                        destination_room = Current_Room([current_room, Grabbable_Dict[pot][1]], Room_List)
                       
                        destination_room_copy = room_copy_dict[destination_room.number]
                       
                        pot_copy = Find_Actor_Copy(pot, Room_List_Copy)
                        superslide_transition_copy = Grabbable_Dict_Copy[pot_copy][1]
                       
                        Load_Room(Heap_Copy, destination_room_copy, superslide_transition_copy, Overlay_Dict_Copy)
                        action_list001.append("Load Room: Room %d" %(destination_room_copy.number) + " with " + superslide_transition_copy.name + " %d" %(superslide_transition_copy.priority))
                       
                        """
                       
                       Now we check all neighbors of our current room (destination_room) and for
                       each neighbor that has a chest or deku guard in it, we will create a copy
                       of our copy of the state, then enter each of them through each possible
                       loading plane and then check the chest/guard addresses and see if anything
                       lines up
                       
                       """
                       
                        for neighbor in Neighbors(destination_room, Room_List):
                           
                            if Chest_In_Room(neighbor) == True or Deku_Guard_In_Room(neighbor) == True:
 
                                for transition in Shared_Transitions(destination_room, neighbor):
 
                                    # COPY STATE
                                    #######################################################
                                    Room_List_Copy_2 = Copy_Room_List(Room_List_Copy)
                                    Overlay_Dict_Copy_2 = Copy_Overlay_Dict(Overlay_Dict_Copy)
                                   
                                    room_copy_dict_2 = {}
                                    for room in Room_List_Copy_2:
                                        room_copy_dict_2[room.number] = room
                                   
                                    Heap_Copy_2 = Copy_Heap(Heap_Copy, Room_List_Copy_2, Overlay_Dict_Copy_2)
                                   
                                    Grabbable_Dict_Copy_2 = Copy_Grabbable_Dict(Grabbable_Dict_Copy, Room_List_Copy_2)
                                    #######################################################
 
                                    action_list_2 = []
                                   
                                    transition_copy = Find_Actor_Copy(transition, Room_List_Copy_2)
                                   
                                    neighbor_copy = room_copy_dict_2[neighbor.number]
                                   
                                    Load_Room(Heap_Copy_2, neighbor_copy, transition_copy, Overlay_Dict_Copy_2)
                                    action_list_2.append("Load Room: Room %d" %(neighbor_copy.number) + " with " + transition_copy.name + " %d" %(transition_copy.priority))
                                   
                                   
                                    ##### Now check for chests/deku guards
                       
                                    chest_guard_list = []
                                   
                                    for entry in Heap_Copy_2:
                                       
                                        if type(entry) == Actor and (entry.Id == '0006' or entry.Id == '017A'):
                                            chest_guard_list.append(entry)
                                   
                                    soln_found = False
                                    for entry in chest_guard_list:
                                        if (pot.address - entry.address) in Offset_List:
                                           
                                            action_list_2.append("SOLUTION: " + pot.name + " (Priority %d)" %(pot.priority) + " from Room %d" %(pot.room_number) + " lines up with " + entry.name + " (Priority %d)" %(entry.priority) + " from Room %d" %(entry.room_number) + " with offset: " + hex(pot.address - entry.address))
 
                                            if (pot.address - entry.address) == 0x160:
                                                angle_solution_count += 1
                                                print("ANGLE SOLUTION FOUND (CHEST)!!!!!!!!!!!")
                                            elif (pot.address - entry.address) == 0x1F0:
                                                position_solution_count += 1
                                                print("Z POSITION SOLUTION FOUND (CHEST)!!!!!!!!!!!")
 
                                            soln_found = True
                                           
                                    if soln_found is True:
                                        total_action_list = action_list + action_list001 + action_list_2
                                       
                                        # the "a" argument is important so we don't overwrite previous solutions
                                        with open(filename, "a") as file:
                                           
                                            for action in total_action_list:
                                               
                                                file.write(action + "\n")
                                            file.write("-----\n")
                       
                       
            ##### Case 3: there is NOT a valid grabbable actor in the current room            
            elif (current_room not in valid_grabbable_actor_room_list):
               
                for neighbor in Neighbors(current_room, Room_List):
                   
                    ##### Valid grabbable actor in neighbor
                    if neighbor in valid_grabbable_actor_room_list:
                       
                       
                        # For every transition in Shared_Transitions(current_room, neighbor)
                        for transition in Shared_Transitions(current_room, neighbor):
                           
                            action_list_transition = []
                           
                            ##### COPY THE STATE
                            #######################################################
                            Room_List_Copy = Copy_Room_List(Room_List)
                            Overlay_Dict_Copy = Copy_Overlay_Dict(Overlay_Dict)
                           
                            room_copy_dict = {}
                            for room in Room_List_Copy:
                                room_copy_dict[room.number] = room
                           
                            Heap_Copy = Copy_Heap(Heap, Room_List_Copy, Overlay_Dict_Copy)
                           
                            Grabbable_Dict_Copy = Copy_Grabbable_Dict(Grabbable_Dict, Room_List_Copy)
                            #######################################################
                           
                            ##### ENTER neighbor after copying it
                           
                            neighbor_copy = room_copy_dict[neighbor.number]
                            transition_copy = Find_Actor_Copy(transition, Room_List_Copy)
 
                            Load_Room(Heap_Copy, neighbor_copy, transition_copy, Overlay_Dict_Copy)
                            action_list_transition.append("Load Room: Room %d" %(neighbor_copy.number) + " with " + transition_copy.name + " %d" %(transition_copy.priority))
                           
                           
                            ##### Iterate through all pots in this room
                       
                            valid_pot_list = []
                            pot_address_list = []
                           
                            for pot in Grabbable_Dict_Copy:
                               
                                if Actor_Is_In_Room(neighbor_copy, pot) is True:
                                    valid_pot_list.append(pot)
                                    pot_address_list.append(pot.address)
                           
                           
                           
                            # If there is a chest/guard, superslide, then check neighbors for chests/guards and test all (copy state)
                            if Chest_In_Room(neighbor) == True or Deku_Guard_In_Room(neighbor) == True:
                               
                                for pot in valid_pot_list:
                                   
                                    # both bomb and smoke loaded on superslide
                                    if Grabbable_Dict_Copy[pot][0][0] == '1':
                                       
                                        action_list100 = []
                                       
                                        # COPY STATE
                                        #######################################################
                                        Room_List_Copy_SS = Copy_Room_List(Room_List_Copy)
                                        Overlay_Dict_Copy_SS = Copy_Overlay_Dict(Overlay_Dict_Copy)
                                       
                                        room_copy_dict_SS = {}
                                        for room in Room_List_Copy_SS:
                                            room_copy_dict_SS[room.number] = room
                                       
                                        Heap_Copy_SS = Copy_Heap(Heap_Copy, Room_List_Copy_SS, Overlay_Dict_Copy_SS)
                                       
                                        Grabbable_Dict_Copy_SS = Copy_Grabbable_Dict(Grabbable_Dict_Copy, Room_List_Copy_SS)
                                        #######################################################
                                       
                                        Bomb_And_Smoke_Superslide(Heap_Copy_SS, neighbor.number, Overlay_Dict_Copy_SS)
                                        action_list100.append("Superslide with Bomb and Smoke still allocated")
                                       
                                        # The room we superslide into through the plane corresponding to the given pot
                                        destination_room = Current_Room([neighbor_copy, Grabbable_Dict_Copy[pot][1]], Room_List_Copy)
                                       
                                        destination_room_copy = room_copy_dict_SS[destination_room.number]
                                       
                                        pot_copy = Find_Actor_Copy(pot, Room_List_Copy_SS)
                                        superslide_transition_copy = Grabbable_Dict_Copy_SS[pot_copy][1]
                                       
                                        Load_Room(Heap_Copy_SS, destination_room_copy, superslide_transition_copy, Overlay_Dict_Copy_SS)
                                        action_list100.append("Load Room: Room %d" %(destination_room_copy.number) + " with " + superslide_transition_copy.name + " %d" %(superslide_transition_copy.priority))
                                       
                                        """
                                       
                                       Now we check all neighbors of our current room (destination_room) and for
                                       each neighbor that has a chest or deku guard in it, we will create a copy
                                       of our copy of the state, then enter each of them through each possible
                                       loading plane and then check the chest/guard addresses and see if anything
                                       lines up
                                       
                                       """
                                       
                                        for bordering_room in Neighbors(destination_room, Room_List):
                                           
                                            if Chest_In_Room(bordering_room) == True or Deku_Guard_In_Room(bordering_room) == True:
                                               
                                                for loading_plane in Shared_Transitions(destination_room, bordering_room):
                                                   
                                                     # COPY STATE
                                                    #######################################################
                                                    Room_List_Copy_2 = Copy_Room_List(Room_List_Copy_SS)
                                                    Overlay_Dict_Copy_2 = Copy_Overlay_Dict(Overlay_Dict_Copy_SS)
                                                   
                                                    room_copy_dict_2 = {}
                                                    for room in Room_List_Copy_2:
                                                        room_copy_dict_2[room.number] = room
                                                   
                                                    Heap_Copy_2 = Copy_Heap(Heap_Copy_SS, Room_List_Copy_2, Overlay_Dict_Copy_2)
                                                   
                                                    Grabbable_Dict_Copy_2 = Copy_Grabbable_Dict(Grabbable_Dict_Copy_SS, Room_List_Copy_2)
                                                    #######################################################
                                                   
                                                    action_list_2 = []
                                                   
                                                    loading_plane_copy = Find_Actor_Copy(loading_plane, Room_List_Copy_2)
                                                   
                                                    bordering_room_copy = room_copy_dict_2[bordering_room.number]
                                                   
                                                    Load_Room(Heap_Copy_2, bordering_room_copy, loading_plane_copy, Overlay_Dict_Copy_2)
                                                    action_list_2.append("Load Room: Room %d" %(bordering_room_copy.number) + " with " + loading_plane_copy.name + " %d" %(loading_plane_copy.priority))
                                                   
                                                   
                                                    ##### Now check for chests/deku guards
                                       
                                                    chest_guard_list = []
                                                   
                                                    for entry in Heap_Copy_2:
                                                       
                                                        if type(entry) == Actor and (entry.Id == '0006' or entry.Id == '017A'):
                                                            chest_guard_list.append(entry)
                                                   
                                                    soln_found = False
                                                    for entry in chest_guard_list:
                                                        if (pot.address - entry.address) in Offset_List:
                                                           
                                                            action_list_2.append("SOLUTION: " + pot.name + " (Priority %d)" %(pot.priority) + " from Room %d" %(pot.room_number) + " lines up with " + entry.name + " (Priority %d)" %(entry.priority) + " from Room %d" %(entry.room_number) + " with offset: " + hex(pot.address - entry.address))
 
                                                            if (pot.address - entry.address) == 0x160:
                                                                angle_solution_count += 1
                                                                print("ANGLE SOLUTION FOUND (CHEST)!!!!!!!!!!!")
                                                            elif (pot.address - entry.address) == 0x1F0:
                                                                position_solution_count += 1
                                                                print("Z POSITION SOLUTION FOUND (CHEST)!!!!!!!!!!!")
 
                                                            soln_found = True
                                                           
                                                    if soln_found is True:
                                                        total_action_list = action_list + action_list_transition + action_list100 + action_list_2
                                                       
                                                        # the "a" argument is important so we don't overwrite previous solutions
                                                        with open(filename, "a") as file:
                                                           
                                                            for action in total_action_list:
                                                               
                                                                file.write(action + "\n")
                                                            file.write("-----\n")
                                   
                                       
                                       
                                    ##### Only smoke is loaded from superslide
                                    elif Grabbable_Dict_Copy[pot][0][1] == '1':
                                       
                                        action_list010 = []
                                       
                                        # COPY STATE
                                        #######################################################
                                        Room_List_Copy_SS = Copy_Room_List(Room_List_Copy)
                                        Overlay_Dict_Copy_SS = Copy_Overlay_Dict(Overlay_Dict_Copy)
                                       
                                        room_copy_dict_SS = {}
                                        for room in Room_List_Copy_SS:
                                            room_copy_dict_SS[room.number] = room
                                       
                                        Heap_Copy_SS = Copy_Heap(Heap_Copy, Room_List_Copy_SS, Overlay_Dict_Copy_SS)
                                       
                                        Grabbable_Dict_Copy_SS = Copy_Grabbable_Dict(Grabbable_Dict_Copy, Room_List_Copy_SS)
                                        #######################################################
                                       
                                        Allocate_Smoke(Heap_Copy_SS, neighbor.number, Overlay_Dict_Copy_SS)
                                        action_list010.append("Superslide with Smoke still allocated")
                                       
                                        # The room we superslide into through the plane corresponding to the given pot
                                        destination_room = Current_Room([neighbor_copy, Grabbable_Dict_Copy[pot][1]], Room_List_Copy)
                                       
                                        destination_room_copy = room_copy_dict_SS[destination_room.number]
                                       
                                        pot_copy = Find_Actor_Copy(pot, Room_List_Copy_SS)
                                        superslide_transition_copy = Grabbable_Dict_Copy_SS[pot_copy][1]
                                       
                                        Load_Room(Heap_Copy_SS, destination_room_copy, superslide_transition_copy, Overlay_Dict_Copy_SS)
                                        action_list010.append("Load Room: Room %d" %(destination_room_copy.number) + " with " + superslide_transition_copy.name + " %d" %(superslide_transition_copy.priority))
                                       
                                        """
                                       
                                       Now we check all neighbors of our current room (destination_room) and for
                                       each neighbor that has a chest or deku guard in it, we will create a copy
                                       of our copy of the state, then enter each of them through each possible
                                       loading plane and then check the chest/guard addresses and see if anything
                                       lines up
                                       
                                       """
                                       
                                        for bordering_room in Neighbors(destination_room, Room_List):
                                           
                                            if Chest_In_Room(bordering_room) == True or Deku_Guard_In_Room(bordering_room) == True:
                                               
                                                for loading_plane in Shared_Transitions(destination_room, bordering_room):
                                                   
                                                     # COPY STATE
                                                    #######################################################
                                                    Room_List_Copy_2 = Copy_Room_List(Room_List_Copy_SS)
                                                    Overlay_Dict_Copy_2 = Copy_Overlay_Dict(Overlay_Dict_Copy_SS)
                                                   
                                                    room_copy_dict_2 = {}
                                                    for room in Room_List_Copy_2:
                                                        room_copy_dict_2[room.number] = room
                                                   
                                                    Heap_Copy_2 = Copy_Heap(Heap_Copy_SS, Room_List_Copy_2, Overlay_Dict_Copy_2)
                                                   
                                                    Grabbable_Dict_Copy_2 = Copy_Grabbable_Dict(Grabbable_Dict_Copy_SS, Room_List_Copy_2)
                                                    #######################################################
                                                   
                                                    action_list_2 = []
                                                   
                                                    loading_plane_copy = Find_Actor_Copy(loading_plane, Room_List_Copy_2)
                                                   
                                                    bordering_room_copy = room_copy_dict_2[bordering_room.number]
                                                   
                                                    Load_Room(Heap_Copy_2, bordering_room_copy, loading_plane_copy, Overlay_Dict_Copy_2)
                                                    action_list_2.append("Load Room: Room %d" %(bordering_room_copy.number) + " with " + loading_plane_copy.name + " %d" %(loading_plane_copy.priority))
                                                   
                                                   
                                                    ##### Now check for chests/deku guards
                                       
                                                    chest_guard_list = []
                                                   
                                                    for entry in Heap_Copy_2:
                                                       
                                                        if type(entry) == Actor and (entry.Id == '0006' or entry.Id == '017A'):
                                                            chest_guard_list.append(entry)
                                                   
                                                    soln_found = False
                                                    for entry in chest_guard_list:
                                                        if (pot.address - entry.address) in Offset_List:
                                                           
                                                            action_list_2.append("SOLUTION: " + pot.name + " (Priority %d)" %(pot.priority) + " from Room %d" %(pot.room_number) + " lines up with " + entry.name + " (Priority %d)" %(entry.priority) + " from Room %d" %(entry.room_number) + " with offset: " + hex(pot.address - entry.address))
                                                           
                                                            if (pot.address - entry.address) == 0x160:
                                                                angle_solution_count += 1
                                                                print("ANGLE SOLUTION FOUND (CHEST)!!!!!!!!!!!")
                                                            elif (pot.address - entry.address) == 0x1F0:
                                                                position_solution_count += 1
                                                                print("Z POSITION SOLUTION FOUND (CHEST)!!!!!!!!!!!")
                               
                                                            soln_found = True
                                                           
                                                    if soln_found is True:
                                                        total_action_list = action_list + action_list_transition + action_list010 + action_list_2
                                                       
                                                        # the "a" argument is important so we don't overwrite previous solutions
                                                        with open(filename, "a") as file:
                                                           
                                                            for action in total_action_list:
                                                               
                                                                file.write(action + "\n")
                                                            file.write("-----\n")
 
 
                                    #### Bomb and Smoke are both unloaded
                                    elif Grabbable_Dict_Copy[pot][0][2] == '1':
                                       
                                        action_list001 = []
                                       
                                        # COPY STATE
                                        #######################################################
                                        Room_List_Copy_SS = Copy_Room_List(Room_List_Copy)
                                        Overlay_Dict_Copy_SS = Copy_Overlay_Dict(Overlay_Dict_Copy)
                                       
                                        room_copy_dict_SS = {}
                                        for room in Room_List_Copy_SS:
                                            room_copy_dict_SS[room.number] = room
                                       
                                        Heap_Copy_SS = Copy_Heap(Heap_Copy, Room_List_Copy_SS, Overlay_Dict_Copy_SS)
                                       
                                        Grabbable_Dict_Copy_SS = Copy_Grabbable_Dict(Grabbable_Dict_Copy, Room_List_Copy_SS)
                                        #######################################################
                                       
                                        # Do not allocate anything
                                        action_list001.append("Superslide with Bomb and Smoke unloaded when passing plane")
                                       
                                        # The room we superslide into through the plane corresponding to the given pot
                                        destination_room = Current_Room([neighbor_copy, Grabbable_Dict_Copy[pot][1]], Room_List_Copy)
                                       
                                        destination_room_copy = room_copy_dict_SS[destination_room.number]
                                       
                                        pot_copy = Find_Actor_Copy(pot, Room_List_Copy_SS)
                                        superslide_transition_copy = Grabbable_Dict_Copy_SS[pot_copy][1]
                                       
                                        Load_Room(Heap_Copy_SS, destination_room_copy, superslide_transition_copy, Overlay_Dict_Copy_SS)
                                        action_list001.append("Load Room: Room %d" %(destination_room_copy.number) + " with " + superslide_transition_copy.name + " %d" %(superslide_transition_copy.priority))
                                       
                                        """
                                       
                                       Now we check all neighbors of our current room (destination_room) and for
                                       each neighbor that has a chest or deku guard in it, we will create a copy
                                       of our copy of the state, then enter each of them through each possible
                                       loading plane and then check the chest/guard addresses and see if anything
                                       lines up
                                       
                                       """
                                       
                                        for bordering_room in Neighbors(destination_room, Room_List):
                                           
                                            if Chest_In_Room(bordering_room) == True or Deku_Guard_In_Room(bordering_room) == True:
                                               
                                                for loading_plane in Shared_Transitions(destination_room, bordering_room):
                                                   
                                                     # COPY STATE
                                                    #######################################################
                                                    Room_List_Copy_2 = Copy_Room_List(Room_List_Copy_SS)
                                                    Overlay_Dict_Copy_2 = Copy_Overlay_Dict(Overlay_Dict_Copy_SS)
                                                   
                                                    room_copy_dict_2 = {}
                                                    for room in Room_List_Copy_2:
                                                        room_copy_dict_2[room.number] = room
                                                   
                                                    Heap_Copy_2 = Copy_Heap(Heap_Copy_SS, Room_List_Copy_2, Overlay_Dict_Copy_2)
                                                   
                                                    Grabbable_Dict_Copy_2 = Copy_Grabbable_Dict(Grabbable_Dict_Copy_SS, Room_List_Copy_2)
                                                    #######################################################
                                                   
                                                    action_list_2 = []
                                                   
                                                    loading_plane_copy = Find_Actor_Copy(loading_plane, Room_List_Copy_2)
                                                   
                                                    bordering_room_copy = room_copy_dict_2[bordering_room.number]
                                                   
                                                    Load_Room(Heap_Copy_2, bordering_room_copy, loading_plane_copy, Overlay_Dict_Copy_2)
                                                    action_list_2.append("Load Room: Room %d" %(bordering_room_copy.number) + " with " + loading_plane_copy.name + " %d" %(loading_plane_copy.priority))
                                                   
                                                   
                                                    ##### Now check for chests/deku guards
                                       
                                                    chest_guard_list = []
                                                   
                                                    for entry in Heap_Copy_2:
                                                       
                                                        if type(entry) == Actor and (entry.Id == '0006' or entry.Id == '017A'):
                                                            chest_guard_list.append(entry)
                                                   
                                                    soln_found = False
                                                    for entry in chest_guard_list:
                                                        if (pot.address - entry.address) in Offset_List:
                                                           
                                                            action_list_2.append("SOLUTION: " + pot.name + " (Priority %d)" %(pot.priority) + " from Room %d" %(pot.room_number) + " lines up with " + entry.name + " (Priority %d)" %(entry.priority) + " from Room %d" %(entry.room_number) + " with offset: " + hex(pot.address - entry.address))
                                                           
                                                            if (pot.address - entry.address) == 0x160:
                                                                angle_solution_count += 1
                                                                print("ANGLE SOLUTION FOUND (CHEST)!!!!!!!!!!!")
                                                            elif (pot.address - entry.address) == 0x1F0:
                                                                position_solution_count += 1
                                                                print("Z POSITION SOLUTION FOUND (CHEST)!!!!!!!!!!!")
                               
                                                            soln_found = True
                                                           
                                                    if soln_found is True:
                                                        total_action_list = action_list + action_list_transition + action_list001 + action_list_2
                                                       
                                                        # the "a" argument is important so we don't overwrite previous solutions
                                                        with open(filename, "a") as file:
                                                           
                                                            for action in total_action_list:
                                                               
                                                                file.write(action + "\n")
                                                            file.write("-----\n")                
 
                                       
                                       
                            # If there isn't a chest/guard, superslide (into chest/guard room by assumption), then exit then reenter it (this case never happens in palace, so this is an okay assumption)
                            elif Chest_In_Room(neighbor) == False and Deku_Guard_In_Room(neighbor) == False:
                               
                                for pot in valid_pot_list:
                                   
                                    # both bomb and smoke loaded on superslide
                                    if Grabbable_Dict_Copy[pot][0][0] == '1':
                                       
                                        action_list100 = []
                                       
                                        # COPY STATE
                                        #######################################################
                                        Room_List_Copy_2 = Copy_Room_List(Room_List_Copy)
                                        Overlay_Dict_Copy_2 = Copy_Overlay_Dict(Overlay_Dict_Copy)
                                       
                                        room_copy_dict_2 = {}
                                        for room in Room_List_Copy_2:
                                            room_copy_dict_2[room.number] = room
                                       
                                        Heap_Copy_2 = Copy_Heap(Heap_Copy, Room_List_Copy_2, Overlay_Dict_Copy_2)
                                       
                                        Grabbable_Dict_Copy_2 = Copy_Grabbable_Dict(Grabbable_Dict_Copy, Room_List_Copy_2)
                                        #######################################################
                                       
                                        Bomb_And_Smoke_Superslide(Heap_Copy_2, neighbor_copy.number, Overlay_Dict_Copy_2)
                                        action_list100.append("Superslide with Bomb and Smoke still allocated")
                                       
                                        # The room we superslide into through the plane corresponding to the given pot
                                        destination_room = Current_Room([neighbor_copy, Grabbable_Dict_Copy[pot][1]], Room_List_Copy)
                                       
                                        destination_room_copy = room_copy_dict_2[destination_room.number]
                                        neighbor_copy_2 = room_copy_dict_2[neighbor_copy.number]
                                       
                                        pot_copy = Find_Actor_Copy(pot, Room_List_Copy_2)
                                        superslide_transition_copy = Grabbable_Dict_Copy_2[pot_copy][1]
                                       
                                        Load_Room(Heap_Copy_2, destination_room_copy, superslide_transition_copy, Overlay_Dict_Copy_2)
                                        action_list100.append("Load Room: Room %d" %(destination_room_copy.number) + " with " + superslide_transition_copy.name + " %d" %(superslide_transition_copy.priority))
                                       
                                        # Now exit the chest room
                                        Load_Room(Heap_Copy_2, neighbor_copy_2, superslide_transition_copy, Overlay_Dict_Copy_2)
                                        action_list100.append("Load Room: Room %d" %(neighbor_copy_2.number) + " with " + superslide_transition_copy.name + " %d" %(superslide_transition_copy.priority))
                                       
                                        # Now reenter the chest room
                                        Load_Room(Heap_Copy_2, destination_room_copy, superslide_transition_copy, Overlay_Dict_Copy_2)
                                        action_list100.append("Load Room: Room %d" %(destination_room_copy.number) + " with " + superslide_transition_copy.name + " %d" %(superslide_transition_copy.priority))
                                       
                                        ##### Now check for chests/deku guards
                                       
                                        chest_guard_list = []
                                       
                                        for entry in Heap_Copy_2:
                                           
                                            if type(entry) == Actor and (entry.Id == '0006' or entry.Id == '017A'):
                                                chest_guard_list.append(entry)
                                       
                                        soln_found = False
                                        for entry in chest_guard_list:
                                            if (pot.address - entry.address) in Offset_List:
                                               
                                                action_list100.append("SOLUTION: " + pot.name + " (Priority %d)" %(pot.priority) + " from Room %d" %(pot.room_number) + " lines up with " + entry.name + " (Priority %d)" %(entry.priority) + " from Room %d" %(entry.room_number) + " with offset: " + hex(pot.address - entry.address))
                                               
                                                if (pot.address - entry.address) == 0x160:
                                                    angle_solution_count += 1
                                                    print("ANGLE SOLUTION FOUND (CHEST)!!!!!!!!!!!")
                                                elif (pot.address - entry.address) == 0x1F0:
                                                    position_solution_count += 1
                                                    print("Z POSITION SOLUTION FOUND (CHEST)!!!!!!!!!!!")
                               
                                                soln_found = True
                                               
                                        if soln_found is True:
                                            total_action_list = action_list + action_list_transition + action_list100
                                           
                                            # the "a" argument is important so we don't overwrite previous solutions
                                            with open(filename, "a") as file:
                                               
                                                for action in total_action_list:
                                                   
                                                    file.write(action + "\n")
                                                file.write("-----\n")
                                   
                                   
                                   
                                    ##### Only smoke is loaded from superslide
                                    elif Grabbable_Dict_Copy[pot][0][1] == '1':
 
                                        action_list010 = []
                                       
                                        # COPY STATE
                                        #######################################################
                                        Room_List_Copy_2 = Copy_Room_List(Room_List_Copy)
                                        Overlay_Dict_Copy_2 = Copy_Overlay_Dict(Overlay_Dict_Copy)
                                       
                                        room_copy_dict_2 = {}
                                        for room in Room_List_Copy_2:
                                            room_copy_dict_2[room.number] = room
                                       
                                        Heap_Copy_2 = Copy_Heap(Heap_Copy, Room_List_Copy_2, Overlay_Dict_Copy_2)
                                       
                                        Grabbable_Dict_Copy_2 = Copy_Grabbable_Dict(Grabbable_Dict_Copy, Room_List_Copy_2)
                                        #######################################################
                                       
                                        Allocate_Smoke(Heap_Copy_2, neighbor_copy.number, Overlay_Dict_Copy_2)
                                        action_list010.append("Superslide with Smoke still allocated")
                                       
                                        # The room we superslide into through the plane corresponding to the given pot
                                        destination_room = Current_Room([neighbor_copy, Grabbable_Dict_Copy[pot][1]], Room_List_Copy)
                                       
                                        destination_room_copy = room_copy_dict_2[destination_room.number]
                                        neighbor_copy_2 = room_copy_dict_2[neighbor_copy.number]
                                       
                                        pot_copy = Find_Actor_Copy(pot, Room_List_Copy_2)
                                        superslide_transition_copy = Grabbable_Dict_Copy_2[pot_copy][1]
                                       
                                        Load_Room(Heap_Copy_2, destination_room_copy, superslide_transition_copy, Overlay_Dict_Copy_2)
                                        action_list010.append("Load Room: Room %d" %(destination_room_copy.number) + " with " + superslide_transition_copy.name + " %d" %(superslide_transition_copy.priority))
                                       
                                        # Now exit the chest room
                                        Load_Room(Heap_Copy_2, neighbor_copy_2, superslide_transition_copy, Overlay_Dict_Copy_2)
                                        action_list010.append("Load Room: Room %d" %(neighbor_copy_2.number) + " with " + superslide_transition_copy.name + " %d" %(superslide_transition_copy.priority))
                                       
                                        # Now reenter the chest room
                                        Load_Room(Heap_Copy_2, destination_room_copy, superslide_transition_copy, Overlay_Dict_Copy_2)
                                        action_list010.append("Load Room: Room %d" %(destination_room_copy.number) + " with " + superslide_transition_copy.name + " %d" %(superslide_transition_copy.priority))
                                       
                                        ##### Now check for chests/deku guards
                                       
                                        chest_guard_list = []
                                       
                                        for entry in Heap_Copy_2:
                                           
                                            if type(entry) == Actor and (entry.Id == '0006' or entry.Id == '017A'):
                                                chest_guard_list.append(entry)
                                       
                                        soln_found = False
                                        for entry in chest_guard_list:
                                            if (pot.address - entry.address) in Offset_List:
                                               
                                                action_list010.append("SOLUTION: " + pot.name + " (Priority %d)" %(pot.priority) + " from Room %d" %(pot.room_number) + " lines up with " + entry.name + " (Priority %d)" %(entry.priority) + " from Room %d" %(entry.room_number) + " with offset: " + hex(pot.address - entry.address))
                                               
                                                if (pot.address - entry.address) == 0x160:
                                                    angle_solution_count += 1
                                                    print("ANGLE SOLUTION FOUND (CHEST)!!!!!!!!!!!")
                                                elif (pot.address - entry.address) == 0x1F0:
                                                    position_solution_count += 1
                                                    print("Z POSITION SOLUTION FOUND (CHEST)!!!!!!!!!!!")
                               
                                                soln_found = True
                                               
                                        if soln_found is True:
                                            total_action_list = action_list + action_list_transition + action_list010
                                           
                                            # the "a" argument is important so we don't overwrite previous solutions
                                            with open(filename, "a") as file:
                                               
                                                for action in total_action_list:
                                                   
                                                    file.write(action + "\n")
                                                file.write("-----\n")
 
 
 
                                    #### Bomb and Smoke are both unloaded
                                    elif Grabbable_Dict_Copy[pot][0][2] == '1':
 
                                        action_list001 = []
                                       
                                        # COPY STATE
                                        #######################################################
                                        Room_List_Copy_2 = Copy_Room_List(Room_List_Copy)
                                        Overlay_Dict_Copy_2 = Copy_Overlay_Dict(Overlay_Dict_Copy)
                                       
                                        room_copy_dict_2 = {}
                                        for room in Room_List_Copy_2:
                                            room_copy_dict_2[room.number] = room
                                       
                                        Heap_Copy_2 = Copy_Heap(Heap_Copy, Room_List_Copy_2, Overlay_Dict_Copy_2)
                                       
                                        Grabbable_Dict_Copy_2 = Copy_Grabbable_Dict(Grabbable_Dict_Copy, Room_List_Copy_2)
                                        #######################################################
                                       
                                        # Do not allocate anything
                                        action_list001.append("Superslide with Bomb and Smoke unloaded when passing plane")
                                       
                                        # The room we superslide into through the plane corresponding to the given pot
                                        destination_room = Current_Room([neighbor_copy, Grabbable_Dict_Copy[pot][1]], Room_List_Copy)
                                       
                                        destination_room_copy = room_copy_dict_2[destination_room.number]
                                        neighbor_copy_2 = room_copy_dict_2[neighbor_copy.number]
                                       
                                        pot_copy = Find_Actor_Copy(pot, Room_List_Copy_2)
                                        superslide_transition_copy = Grabbable_Dict_Copy_2[pot_copy][1]
                                       
                                        Load_Room(Heap_Copy_2, destination_room_copy, superslide_transition_copy, Overlay_Dict_Copy_2)
                                        action_list001.append("Load Room: Room %d" %(destination_room_copy.number) + " with " + superslide_transition_copy.name + " %d" %(superslide_transition_copy.priority))
                                       
                                        # Now exit the chest room
                                        Load_Room(Heap_Copy_2, neighbor_copy_2, superslide_transition_copy, Overlay_Dict_Copy_2)
                                        action_list001.append("Load Room: Room %d" %(neighbor_copy_2.number) + " with " + superslide_transition_copy.name + " %d" %(superslide_transition_copy.priority))
                                       
                                        # Now reenter the chest room
                                        Load_Room(Heap_Copy_2, destination_room_copy, superslide_transition_copy, Overlay_Dict_Copy_2)
                                        action_list001.append("Load Room: Room %d" %(destination_room_copy.number) + " with " + superslide_transition_copy.name + " %d" %(superslide_transition_copy.priority))
                                       
                                        ##### Now check for chests/deku guards
                                       
                                        chest_guard_list = []
                                       
                                        for entry in Heap_Copy_2:
                                           
                                            if type(entry) == Actor and (entry.Id == '0006' or entry.Id == '017A'):
                                                chest_guard_list.append(entry)
                                       
                                        soln_found = False
                                        for entry in chest_guard_list:
                                            if (pot.address - entry.address) in Offset_List:
                                               
                                                action_list001.append("SOLUTION: " + pot.name + " (Priority %d)" %(pot.priority) + " from Room %d" %(pot.room_number) + " lines up with " + entry.name + " (Priority %d)" %(entry.priority) + " from Room %d" %(entry.room_number) + " with offset: " + hex(pot.address - entry.address))
                                               
                                                if (pot.address - entry.address) == 0x160:
                                                    angle_solution_count += 1
                                                    print("ANGLE SOLUTION FOUND (CHEST)!!!!!!!!!!!")
                                                elif (pot.address - entry.address) == 0x1F0:
                                                    position_solution_count += 1
                                                    print("Z POSITION SOLUTION FOUND (CHEST)!!!!!!!!!!!")
                               
                                                soln_found = True
                                               
                                        if soln_found is True:
                                            total_action_list = action_list + action_list_transition + action_list001
                                           
                                            # the "a" argument is important so we don't overwrite previous solutions
                                            with open(filename, "a") as file:
                                               
                                                for action in total_action_list:
                                                   
                                                    file.write(action + "\n")
                                                file.write("-----\n")
                                       
 
                    ##### No valid grabbable actor in neighbor
                    elif neighbor not in valid_grabbable_actor_room_list:
                       
                        for new_neighbor in Neighbors(neighbor, Room_List):
                           
                            # if new neighbor has a valid grabbable actor... (Otherwise, we do nothing)
                            if new_neighbor in valid_grabbable_actor_room_list:
                               
                               
                                for neighbor_transition in Shared_Transitions(current_room, neighbor):
                                    for new_neighbor_transition in Shared_Transitions(neighbor, new_neighbor):
                                       
                                        action_list_transition = []
                               
                                        ##### COPY THE STATE
                                        #######################################################
                                        Room_List_Copy = Copy_Room_List(Room_List)
                                        Overlay_Dict_Copy = Copy_Overlay_Dict(Overlay_Dict)
                                       
                                        room_copy_dict = {}
                                        for room in Room_List_Copy:
                                            room_copy_dict[room.number] = room
                                       
                                        Heap_Copy = Copy_Heap(Heap, Room_List_Copy, Overlay_Dict_Copy)
                                       
                                        Grabbable_Dict_Copy = Copy_Grabbable_Dict(Grabbable_Dict, Room_List_Copy)
                                        #######################################################
                                       
                                        neighbor_copy = room_copy_dict[neighbor.number]
                                        neighbor_transition_copy = Find_Actor_Copy(neighbor_transition, Room_List_Copy)
                                       
                                        new_neighbor_copy = room_copy_dict[new_neighbor.number]
                                        new_neighbor_transition_copy = Find_Actor_Copy(new_neighbor_transition, Room_List_Copy)
                                                                       
                                        ##### ENTER neighbor
                                       
                                        Load_Room(Heap_Copy, neighbor_copy, neighbor_transition_copy, Overlay_Dict_Copy)
                                        action_list_transition.append("Load Room: Room %d" %(neighbor_copy.number) + " with " + neighbor_transition_copy.name + " %d" %(neighbor_transition_copy.priority))
                                       
                                        ##### ENTER new_neighbor
                                       
                                        Load_Room(Heap_Copy, new_neighbor_copy, new_neighbor_transition_copy, Overlay_Dict_Copy)
                                        action_list_transition.append("Load Room: Room %d" %(new_neighbor_copy.number) + " with " + new_neighbor_transition_copy.name + " %d" %(new_neighbor_transition_copy.priority))
                                       
                                       
                                        ##### Iterate through all pots in this room
                               
                                        valid_pot_list = []
                                        pot_address_list = []
                                       
                                        for pot in Grabbable_Dict_Copy:
                                           
                                            if Actor_Is_In_Room(new_neighbor_copy, pot) is True:
                                                valid_pot_list.append(pot)
                                                pot_address_list.append(pot.address)
 
                                        # If there is a chest/guard, superslide, then check neighbors for chests/guards and test all (copy state)
                                        if Chest_In_Room(new_neighbor) == True or Deku_Guard_In_Room(new_neighbor) == True:
                                           
                                            for pot in valid_pot_list:
                                               
                                                # both bomb and smoke loaded on superslide
                                                if Grabbable_Dict_Copy[pot][0][0] == '1':
                                                   
                                                    action_list100 = []
                                                   
                                                    # COPY STATE
                                                    #######################################################
                                                    Room_List_Copy_SS = Copy_Room_List(Room_List_Copy)
                                                    Overlay_Dict_Copy_SS = Copy_Overlay_Dict(Overlay_Dict_Copy)
                                                   
                                                    room_copy_dict_SS = {}
                                                    for room in Room_List_Copy_SS:
                                                        room_copy_dict_SS[room.number] = room
                                                   
                                                    Heap_Copy_SS = Copy_Heap(Heap_Copy, Room_List_Copy_SS, Overlay_Dict_Copy_SS)
                                                   
                                                    Grabbable_Dict_Copy_SS = Copy_Grabbable_Dict(Grabbable_Dict_Copy, Room_List_Copy_SS)
                                                    #######################################################
                                                   
                                                    Bomb_And_Smoke_Superslide(Heap_Copy_SS, new_neighbor.number, Overlay_Dict_Copy_SS)
                                                    action_list100.append("Superslide with Bomb and Smoke still allocated")
                                                   
                                                    # The room we superslide into through the plane corresponding to the given pot
                                                    destination_room = Current_Room([new_neighbor_copy, Grabbable_Dict_Copy[pot][1]], Room_List_Copy)
                                                   
                                                    destination_room_copy = room_copy_dict_SS[destination_room.number]
                                                   
                                                    pot_copy = Find_Actor_Copy(pot, Room_List_Copy_SS)
                                                    superslide_transition_copy = Grabbable_Dict_Copy_SS[pot_copy][1]
                                                   
                                                    Load_Room(Heap_Copy_SS, destination_room_copy, superslide_transition_copy, Overlay_Dict_Copy_SS)
                                                    action_list100.append("Load Room: Room %d" %(destination_room_copy.number) + " with " + superslide_transition_copy.name + " %d" %(superslide_transition_copy.priority))
                                                   
                                                    """
                                                   
                                                   Now we check all neighbors of our current room (destination_room) and for
                                                   each neighbor that has a chest or deku guard in it, we will create a copy
                                                   of our copy of the state, then enter each of them through each possible
                                                   loading plane and then check the chest/guard addresses and see if anything
                                                   lines up
                                                   
                                                   """
                                                   
                                                    for bordering_room in Neighbors(destination_room, Room_List):
                                                       
                                                        if Chest_In_Room(bordering_room) == True or Deku_Guard_In_Room(bordering_room) == True:
                                                           
                                                            for loading_plane in Shared_Transitions(destination_room, bordering_room):
                                                               
                                                                 # COPY STATE
                                                                #######################################################
                                                                Room_List_Copy_2 = Copy_Room_List(Room_List_Copy_SS)
                                                                Overlay_Dict_Copy_2 = Copy_Overlay_Dict(Overlay_Dict_Copy_SS)
                                                               
                                                                room_copy_dict_2 = {}
                                                                for room in Room_List_Copy_2:
                                                                    room_copy_dict_2[room.number] = room
                                                               
                                                                Heap_Copy_2 = Copy_Heap(Heap_Copy_SS, Room_List_Copy_2, Overlay_Dict_Copy_2)
                                                               
                                                                Grabbable_Dict_Copy_2 = Copy_Grabbable_Dict(Grabbable_Dict_Copy_SS, Room_List_Copy_2)
                                                                #######################################################
                                                               
                                                                action_list_2 = []
                                                               
                                                                loading_plane_copy = Find_Actor_Copy(loading_plane, Room_List_Copy_2)
                                                               
                                                                bordering_room_copy = room_copy_dict_2[bordering_room.number]
                                                               
                                                                Load_Room(Heap_Copy_2, bordering_room_copy, loading_plane_copy, Overlay_Dict_Copy_2)
                                                                action_list_2.append("Load Room: Room %d" %(bordering_room_copy.number) + " with " + loading_plane_copy.name + " %d" %(loading_plane_copy.priority))
                                                               
                                                               
                                                                ##### Now check for chests/deku guards
                                                   
                                                                chest_guard_list = []
                                                               
                                                                for entry in Heap_Copy_2:
                                                                   
                                                                    if type(entry) == Actor and (entry.Id == '0006' or entry.Id == '017A'):
                                                                        chest_guard_list.append(entry)
                                                               
                                                                soln_found = False
                                                                for entry in chest_guard_list:
                                                                    if (pot.address - entry.address) in Offset_List:
                                                                       
                                                                        action_list_2.append("SOLUTION: " + pot.name + " (Priority %d)" %(pot.priority) + " from Room %d" %(pot.room_number) + " lines up with " + entry.name + " (Priority %d)" %(entry.priority) + " from Room %d" %(entry.room_number) + " with offset: " + hex(pot.address - entry.address))
                                                                       
                                                                        if (pot.address - entry.address) == 0x160:
                                                                            angle_solution_count += 1
                                                                            print("ANGLE SOLUTION FOUND (CHEST)!!!!!!!!!!!")
                                                                        elif (pot.address - entry.address) == 0x1F0:
                                                                            position_solution_count += 1
                                                                            print("Z POSITION SOLUTION FOUND (CHEST)!!!!!!!!!!!")
                               
                                                                        soln_found = True
                                                                       
                                                                if soln_found is True:
                                                                    total_action_list = action_list + action_list_transition + action_list100 + action_list_2
                                                                   
                                                                    # the "a" argument is important so we don't overwrite previous solutions
                                                                    with open(filename, "a") as file:
                                                                       
                                                                        for action in total_action_list:
                                                                           
                                                                            file.write(action + "\n")
                                                                        file.write("-----\n")
                                               
                                                   
                                                   
                                                ##### Only smoke is loaded from superslide
                                                elif Grabbable_Dict_Copy[pot][0][1] == '1':
                                                   
                                                    action_list010 = []
                                                   
                                                    # COPY STATE
                                                    #######################################################
                                                    Room_List_Copy_SS = Copy_Room_List(Room_List_Copy)
                                                    Overlay_Dict_Copy_SS = Copy_Overlay_Dict(Overlay_Dict_Copy)
                                                   
                                                    room_copy_dict_SS = {}
                                                    for room in Room_List_Copy_SS:
                                                        room_copy_dict_SS[room.number] = room
                                                   
                                                    Heap_Copy_SS = Copy_Heap(Heap_Copy, Room_List_Copy_SS, Overlay_Dict_Copy_SS)
                                                   
                                                    Grabbable_Dict_Copy_SS = Copy_Grabbable_Dict(Grabbable_Dict_Copy, Room_List_Copy_SS)
                                                    #######################################################
                                                   
                                                    Allocate_Smoke(Heap_Copy_SS, new_neighbor.number, Overlay_Dict_Copy_SS)
                                                    action_list010.append("Superslide with Smoke still allocated")
                                                   
                                                    # The room we superslide into through the plane corresponding to the given pot
                                                    destination_room = Current_Room([new_neighbor_copy, Grabbable_Dict_Copy[pot][1]], Room_List_Copy)
                                                   
                                                    destination_room_copy = room_copy_dict_SS[destination_room.number]
                                                   
                                                    pot_copy = Find_Actor_Copy(pot, Room_List_Copy_SS)
                                                    superslide_transition_copy = Grabbable_Dict_Copy_SS[pot_copy][1]
                                                   
                                                    Load_Room(Heap_Copy_SS, destination_room_copy, superslide_transition_copy, Overlay_Dict_Copy_SS)
                                                    action_list010.append("Load Room: Room %d" %(destination_room_copy.number) + " with " + superslide_transition_copy.name + " %d" %(superslide_transition_copy.priority))
                                                   
                                                    """
                                                   
                                                   Now we check all neighbors of our current room (destination_room) and for
                                                   each neighbor that has a chest or deku guard in it, we will create a copy
                                                   of our copy of the state, then enter each of them through each possible
                                                   loading plane and then check the chest/guard addresses and see if anything
                                                   lines up
                                                   
                                                   """
                                                   
                                                    for bordering_room in Neighbors(destination_room, Room_List):
                                                       
                                                        if Chest_In_Room(bordering_room) == True or Deku_Guard_In_Room(bordering_room) == True:
                                                           
                                                            for loading_plane in Shared_Transitions(destination_room, bordering_room):
                                                               
                                                                 # COPY STATE
                                                                #######################################################
                                                                Room_List_Copy_2 = Copy_Room_List(Room_List_Copy_SS)
                                                                Overlay_Dict_Copy_2 = Copy_Overlay_Dict(Overlay_Dict_Copy_SS)
                                                               
                                                                room_copy_dict_2 = {}
                                                                for room in Room_List_Copy_2:
                                                                    room_copy_dict_2[room.number] = room
                                                               
                                                                Heap_Copy_2 = Copy_Heap(Heap_Copy_SS, Room_List_Copy_2, Overlay_Dict_Copy_2)
                                                               
                                                                Grabbable_Dict_Copy_2 = Copy_Grabbable_Dict(Grabbable_Dict_Copy_SS, Room_List_Copy_2)
                                                                #######################################################
                                                               
                                                                action_list_2 = []
                                                               
                                                                loading_plane_copy = Find_Actor_Copy(loading_plane, Room_List_Copy_2)
                                                               
                                                                bordering_room_copy = room_copy_dict_2[bordering_room.number]
                                                               
                                                                Load_Room(Heap_Copy_2, bordering_room_copy, loading_plane_copy, Overlay_Dict_Copy_2)
                                                                action_list_2.append("Load Room: Room %d" %(bordering_room_copy.number) + " with " + loading_plane_copy.name + " %d" %(loading_plane_copy.priority))
                                                               
                                                               
                                                                ##### Now check for chests/deku guards
                                                   
                                                                chest_guard_list = []
                                                               
                                                                for entry in Heap_Copy_2:
                                                                   
                                                                    if type(entry) == Actor and (entry.Id == '0006' or entry.Id == '017A'):
                                                                        chest_guard_list.append(entry)
                                                               
                                                                soln_found = False
                                                                for entry in chest_guard_list:
                                                                    if (pot.address - entry.address) in Offset_List:
                                                                       
                                                                        action_list_2.append("SOLUTION: " + pot.name + " (Priority %d)" %(pot.priority) + " from Room %d" %(pot.room_number) + " lines up with " + entry.name + " (Priority %d)" %(entry.priority) + " from Room %d" %(entry.room_number) + " with offset: " + hex(pot.address - entry.address))
                                                                       
                                                                        if (pot.address - entry.address) == 0x160:
                                                                            angle_solution_count += 1
                                                                            print("ANGLE SOLUTION FOUND (CHEST)!!!!!!!!!!!")
                                                                        elif (pot.address - entry.address) == 0x1F0:
                                                                            position_solution_count += 1
                                                                            print("Z POSITION SOLUTION FOUND (CHEST)!!!!!!!!!!!")
                               
                                                                        soln_found = True
                                                                       
                                                                if soln_found is True:
                                                                    total_action_list = action_list + action_list_transition + action_list010 + action_list_2
                                                                   
                                                                    # the "a" argument is important so we don't overwrite previous solutions
                                                                    with open(filename, "a") as file:
                                                                       
                                                                        for action in total_action_list:
                                                                           
                                                                            file.write(action + "\n")
                                                                        file.write("-----\n")
           
           
                                                #### Bomb and Smoke are both unloaded
                                                elif Grabbable_Dict_Copy[pot][0][2] == '1':
                                                   
                                                    action_list001 = []
                                                   
                                                    # COPY STATE
                                                    #######################################################
                                                    Room_List_Copy_SS = Copy_Room_List(Room_List_Copy)
                                                    Overlay_Dict_Copy_SS = Copy_Overlay_Dict(Overlay_Dict_Copy)
                                                   
                                                    room_copy_dict_SS = {}
                                                    for room in Room_List_Copy_SS:
                                                        room_copy_dict_SS[room.number] = room
                                                   
                                                    Heap_Copy_SS = Copy_Heap(Heap_Copy, Room_List_Copy_SS, Overlay_Dict_Copy_SS)
                                                   
                                                    Grabbable_Dict_Copy_SS = Copy_Grabbable_Dict(Grabbable_Dict_Copy, Room_List_Copy_SS)
                                                    #######################################################
                                                   
                                                    # Do not allocate anything
                                                    action_list001.append("Superslide with Bomb and Smoke unloaded when passing plane")
                                                   
                                                    # The room we superslide into through the plane corresponding to the given pot
                                                    destination_room = Current_Room([new_neighbor_copy, Grabbable_Dict_Copy[pot][1]], Room_List_Copy)
                                                   
                                                    destination_room_copy = room_copy_dict_SS[destination_room.number]
                                                   
                                                    pot_copy = Find_Actor_Copy(pot, Room_List_Copy_SS)
                                                    superslide_transition_copy = Grabbable_Dict_Copy_SS[pot_copy][1]
                                                   
                                                    Load_Room(Heap_Copy_SS, destination_room_copy, superslide_transition_copy, Overlay_Dict_Copy_SS)
                                                    action_list001.append("Load Room: Room %d" %(destination_room_copy.number) + " with " + superslide_transition_copy.name + " %d" %(superslide_transition_copy.priority))
                                                   
                                                    """
                                                   
                                                   Now we check all neighbors of our current room (destination_room) and for
                                                   each neighbor that has a chest or deku guard in it, we will create a copy
                                                   of our copy of the state, then enter each of them through each possible
                                                   loading plane and then check the chest/guard addresses and see if anything
                                                   lines up
                                                   
                                                   """
                                                   
                                                    for bordering_room in Neighbors(destination_room, Room_List):
                                                       
                                                        if Chest_In_Room(bordering_room) == True or Deku_Guard_In_Room(bordering_room) == True:
                                                           
                                                            for loading_plane in Shared_Transitions(destination_room, bordering_room):
                                                               
                                                                 # COPY STATE
                                                                #######################################################
                                                                Room_List_Copy_2 = Copy_Room_List(Room_List_Copy_SS)
                                                                Overlay_Dict_Copy_2 = Copy_Overlay_Dict(Overlay_Dict_Copy_SS)
                                                               
                                                                room_copy_dict_2 = {}
                                                                for room in Room_List_Copy_2:
                                                                    room_copy_dict_2[room.number] = room
                                                               
                                                                Heap_Copy_2 = Copy_Heap(Heap_Copy_SS, Room_List_Copy_2, Overlay_Dict_Copy_2)
                                                               
                                                                Grabbable_Dict_Copy_2 = Copy_Grabbable_Dict(Grabbable_Dict_Copy_SS, Room_List_Copy_2)
                                                                #######################################################
                                                               
                                                                action_list_2 = []
                                                               
                                                                loading_plane_copy = Find_Actor_Copy(loading_plane, Room_List_Copy_2)
                                                               
                                                                bordering_room_copy = room_copy_dict_2[bordering_room.number]
                                                               
                                                                Load_Room(Heap_Copy_2, bordering_room_copy, loading_plane_copy, Overlay_Dict_Copy_2)
                                                                action_list_2.append("Load Room: Room %d" %(bordering_room_copy.number) + " with " + loading_plane_copy.name + " %d" %(loading_plane_copy.priority))
                                                               
                                                               
                                                                ##### Now check for chests/deku guards
                                                   
                                                                chest_guard_list = []
                                                               
                                                                for entry in Heap_Copy_2:
                                                                   
                                                                    if type(entry) == Actor and (entry.Id == '0006' or entry.Id == '017A'):
                                                                        chest_guard_list.append(entry)
                                                               
                                                                soln_found = False
                                                                for entry in chest_guard_list:
                                                                    if (pot.address - entry.address) in Offset_List:
                                                                       
                                                                        action_list_2.append("SOLUTION: " + pot.name + " (Priority %d)" %(pot.priority) + " from Room %d" %(pot.room_number) + " lines up with " + entry.name + " (Priority %d)" %(entry.priority) + " from Room %d" %(entry.room_number) + " with offset: " + hex(pot.address - entry.address))
                                                                       
                                                                        if (pot.address - entry.address) == 0x160:
                                                                            angle_solution_count += 1
                                                                            print("ANGLE SOLUTION FOUND (CHEST)!!!!!!!!!!!")
                                                                        elif (pot.address - entry.address) == 0x1F0:
                                                                            position_solution_count += 1
                                                                            print("Z POSITION SOLUTION FOUND (CHEST)!!!!!!!!!!!")
                               
                                                                        soln_found = True
                                                                       
                                                                if soln_found is True:
                                                                    total_action_list = action_list + action_list_transition + action_list001 + action_list_2
                                                                   
                                                                    # the "a" argument is important so we don't overwrite previous solutions
                                                                    with open(filename, "a") as file:
                                                                       
                                                                        for action in total_action_list:
                                                                           
                                                                            file.write(action + "\n")
                                                                        file.write("-----\n")
                                               
                                               
                                               
                                        # If there isn't a chest/guard, superslide (into chest/guard room by assumption), then exit then reenter it (this case never happens in palace, so this is an okay assumption)
                                        elif Chest_In_Room(new_neighbor) == False and Deku_Guard_In_Room(new_neighbor) == False:
                                           
                                            for pot in valid_pot_list:
                                               
                                                # both bomb and smoke loaded on superslide
                                                if Grabbable_Dict_Copy[pot][0][0] == '1':
                                                   
                                                    action_list100 = []
                                                   
                                                    # COPY STATE
                                                    #######################################################
                                                    Room_List_Copy_2 = Copy_Room_List(Room_List_Copy)
                                                    Overlay_Dict_Copy_2 = Copy_Overlay_Dict(Overlay_Dict_Copy)
                                                   
                                                    room_copy_dict_2 = {}
                                                    for room in Room_List_Copy_2:
                                                        room_copy_dict_2[room.number] = room
                                                   
                                                    Heap_Copy_2 = Copy_Heap(Heap_Copy, Room_List_Copy_2, Overlay_Dict_Copy_2)
                                                   
                                                    Grabbable_Dict_Copy_2 = Copy_Grabbable_Dict(Grabbable_Dict_Copy, Room_List_Copy_2)
                                                    #######################################################
                                                   
                                                    Bomb_And_Smoke_Superslide(Heap_Copy_2, new_neighbor_copy.number, Overlay_Dict_Copy_2)
                                                    action_list100.append("Superslide with Bomb and Smoke still allocated")
                                                   
                                                    # The room we superslide into through the plane corresponding to the given pot
                                                    destination_room = Current_Room([new_neighbor_copy, Grabbable_Dict_Copy[pot][1]], Room_List_Copy)
                                                   
                                                    destination_room_copy = room_copy_dict_2[destination_room.number]
                                                    new_neighbor_copy_2 = room_copy_dict_2[new_neighbor_copy.number]
                                                   
                                                    pot_copy = Find_Actor_Copy(pot, Room_List_Copy_2)
                                                    superslide_transition_copy = Grabbable_Dict_Copy_2[pot_copy][1]
                                                   
                                                    Load_Room(Heap_Copy_2, destination_room_copy, superslide_transition_copy, Overlay_Dict_Copy_2)
                                                    action_list100.append("Load Room: Room %d" %(destination_room_copy.number) + " with " + superslide_transition_copy.name + " %d" %(superslide_transition_copy.priority))
                                                   
                                                    # Now exit the chest room
                                                    Load_Room(Heap_Copy_2, new_neighbor_copy_2, superslide_transition_copy, Overlay_Dict_Copy_2)
                                                    action_list100.append("Load Room: Room %d" %(new_neighbor_copy_2.number) + " with " + superslide_transition_copy.name + " %d" %(superslide_transition_copy.priority))
                                                   
                                                    # Now reenter the chest room
                                                    Load_Room(Heap_Copy_2, destination_room_copy, superslide_transition_copy, Overlay_Dict_Copy_2)
                                                    action_list100.append("Load Room: Room %d" %(destination_room_copy.number) + " with " + superslide_transition_copy.name + " %d" %(superslide_transition_copy.priority))
                                                   
                                                    ##### Now check for chests/deku guards
                                                   
                                                    chest_guard_list = []
                                                   
                                                    for entry in Heap_Copy_2:
                                                       
                                                        if type(entry) == Actor and (entry.Id == '0006' or entry.Id == '017A'):
                                                            chest_guard_list.append(entry)
                                                   
                                                    soln_found = False
                                                    for entry in chest_guard_list:
                                                        if (pot.address - entry.address) in Offset_List:
                                                           
                                                            action_list100.append("SOLUTION: " + pot.name + " (Priority %d)" %(pot.priority) + " from Room %d" %(pot.room_number) + " lines up with " + entry.name + " (Priority %d)" %(entry.priority) + " from Room %d" %(entry.room_number) + " with offset: " + hex(pot.address - entry.address))
                                                           
                                                            if (pot.address - entry.address) == 0x160:
                                                                angle_solution_count += 1
                                                                print("ANGLE SOLUTION FOUND (CHEST)!!!!!!!!!!!")
                                                            elif (pot.address - entry.address) == 0x1F0:
                                                                position_solution_count += 1
                                                                print("Z POSITION SOLUTION FOUND (CHEST)!!!!!!!!!!!")
                               
                                                            soln_found = True
                                                           
                                                    if soln_found is True:
                                                        total_action_list = action_list + action_list_transition + action_list100
                                                       
                                                        # the "a" argument is important so we don't overwrite previous solutions
                                                        with open(filename, "a") as file:
                                                           
                                                            for action in total_action_list:
                                                               
                                                                file.write(action + "\n")
                                                            file.write("-----\n")
                                               
                                               
                                               
                                                ##### Only smoke is loaded from superslide
                                                elif Grabbable_Dict_Copy[pot][0][1] == '1':
           
                                                    action_list010 = []
                                                   
                                                    # COPY STATE
                                                    #######################################################
                                                    Room_List_Copy_2 = Copy_Room_List(Room_List_Copy)
                                                    Overlay_Dict_Copy_2 = Copy_Overlay_Dict(Overlay_Dict_Copy)
                                                   
                                                    room_copy_dict_2 = {}
                                                    for room in Room_List_Copy_2:
                                                        room_copy_dict_2[room.number] = room
                                                   
                                                    Heap_Copy_2 = Copy_Heap(Heap_Copy, Room_List_Copy_2, Overlay_Dict_Copy_2)
                                                   
                                                    Grabbable_Dict_Copy_2 = Copy_Grabbable_Dict(Grabbable_Dict_Copy, Room_List_Copy_2)
                                                    #######################################################
                                                   
                                                    Allocate_Smoke(Heap_Copy_2, new_neighbor_copy.number, Overlay_Dict_Copy_2)
                                                    action_list010.append("Superslide with Smoke still allocated")
                                                   
                                                    # The room we superslide into through the plane corresponding to the given pot
                                                    destination_room = Current_Room([new_neighbor_copy, Grabbable_Dict_Copy[pot][1]], Room_List_Copy)
                                                   
                                                    destination_room_copy = room_copy_dict_2[destination_room.number]
                                                    new_neighbor_copy_2 = room_copy_dict_2[new_neighbor_copy.number]
                                                   
                                                    pot_copy = Find_Actor_Copy(pot, Room_List_Copy_2)
                                                    superslide_transition_copy = Grabbable_Dict_Copy_2[pot_copy][1]
                                                   
                                                    Load_Room(Heap_Copy_2, destination_room_copy, superslide_transition_copy, Overlay_Dict_Copy_2)
                                                    action_list010.append("Load Room: Room %d" %(destination_room_copy.number) + " with " + superslide_transition_copy.name + " %d" %(superslide_transition_copy.priority))
                                                   
                                                    # Now exit the chest room
                                                    Load_Room(Heap_Copy_2, new_neighbor_copy_2, superslide_transition_copy, Overlay_Dict_Copy_2)
                                                    action_list010.append("Load Room: Room %d" %(new_neighbor_copy_2.number) + " with " + superslide_transition_copy.name + " %d" %(superslide_transition_copy.priority))
                                                   
                                                    # Now reenter the chest room
                                                    Load_Room(Heap_Copy_2, destination_room_copy, superslide_transition_copy, Overlay_Dict_Copy_2)
                                                    action_list010.append("Load Room: Room %d" %(destination_room_copy.number) + " with " + superslide_transition_copy.name + " %d" %(superslide_transition_copy.priority))
                                                   
                                                    ##### Now check for chests/deku guards
                                                   
                                                    chest_guard_list = []
                                                   
                                                    for entry in Heap_Copy_2:
                                                       
                                                        if type(entry) == Actor and (entry.Id == '0006' or entry.Id == '017A'):
                                                            chest_guard_list.append(entry)
                                                   
                                                    soln_found = False
                                                    for entry in chest_guard_list:
                                                        if (pot.address - entry.address) in Offset_List:
                                                           
                                                            action_list010.append("SOLUTION: " + pot.name + " (Priority %d)" %(pot.priority) + " from Room %d" %(pot.room_number) + " lines up with " + entry.name + " (Priority %d)" %(entry.priority) + " from Room %d" %(entry.room_number) + " with offset: " + hex(pot.address - entry.address))
                                                           
                                                            if (pot.address - entry.address) == 0x160:
                                                                angle_solution_count += 1
                                                                print("ANGLE SOLUTION FOUND (CHEST)!!!!!!!!!!!")
                                                            elif (pot.address - entry.address) == 0x1F0:
                                                                position_solution_count += 1
                                                                print("Z POSITION SOLUTION FOUND (CHEST)!!!!!!!!!!!")
                               
                                                            soln_found = True
                                                           
                                                    if soln_found is True:
                                                        total_action_list = action_list + action_list_transition + action_list010
                                                       
                                                        # the "a" argument is important so we don't overwrite previous solutions
                                                        with open(filename, "a") as file:
                                                           
                                                            for action in total_action_list:
                                                               
                                                                file.write(action + "\n")
                                                            file.write("-----\n")
           
           
           
                                                #### Bomb and Smoke are both unloaded
                                                elif Grabbable_Dict_Copy[pot][0][2] == '1':
           
                                                    action_list001 = []
                                                   
                                                    # COPY STATE
                                                    #######################################################
                                                    Room_List_Copy_2 = Copy_Room_List(Room_List_Copy)
                                                    Overlay_Dict_Copy_2 = Copy_Overlay_Dict(Overlay_Dict_Copy)
                                                   
                                                    room_copy_dict_2 = {}
                                                    for room in Room_List_Copy_2:
                                                        room_copy_dict_2[room.number] = room
                                                   
                                                    Heap_Copy_2 = Copy_Heap(Heap_Copy, Room_List_Copy_2, Overlay_Dict_Copy_2)
                                                   
                                                    Grabbable_Dict_Copy_2 = Copy_Grabbable_Dict(Grabbable_Dict_Copy, Room_List_Copy_2)
                                                    #######################################################
                                                   
                                                    # Do not allocate anything
                                                    action_list001.append("Superslide with Bomb and Smoke unloaded when passing plane")
                                                   
                                                    # The room we superslide into through the plane corresponding to the given pot
                                                    destination_room = Current_Room([new_neighbor_copy, Grabbable_Dict_Copy[pot][1]], Room_List_Copy)
                                                   
                                                    destination_room_copy = room_copy_dict_2[destination_room.number]
                                                    new_neighbor_copy_2 = room_copy_dict_2[new_neighbor_copy.number]
                                                   
                                                    pot_copy = Find_Actor_Copy(pot, Room_List_Copy_2)
                                                    superslide_transition_copy = Grabbable_Dict_Copy_2[pot_copy][1]
                                                   
                                                    Load_Room(Heap_Copy_2, destination_room_copy, superslide_transition_copy, Overlay_Dict_Copy_2)
                                                    action_list001.append("Load Room: Room %d" %(destination_room_copy.number) + " with " + superslide_transition_copy.name + " %d" %(superslide_transition_copy.priority))
                                                   
                                                    # Now exit the chest room
                                                    Load_Room(Heap_Copy_2, new_neighbor_copy_2, superslide_transition_copy, Overlay_Dict_Copy_2)
                                                    action_list001.append("Load Room: Room %d" %(new_neighbor_copy_2.number) + " with " + superslide_transition_copy.name + " %d" %(superslide_transition_copy.priority))
                                                   
                                                    # Now reenter the chest room
                                                    Load_Room(Heap_Copy_2, destination_room_copy, superslide_transition_copy, Overlay_Dict_Copy_2)
                                                    action_list001.append("Load Room: Room %d" %(destination_room_copy.number) + " with " + superslide_transition_copy.name + " %d" %(superslide_transition_copy.priority))
                                                   
                                                    ##### Now check for chests/deku guards
                                                   
                                                    chest_guard_list = []
                                                   
                                                    for entry in Heap_Copy_2:
                                                       
                                                        if type(entry) == Actor and (entry.Id == '0006' or entry.Id == '017A'):
                                                            chest_guard_list.append(entry)
                                                   
                                                    soln_found = False
                                                    for entry in chest_guard_list:
                                                        if (pot.address - entry.address) in Offset_List:
                                                           
                                                            action_list001.append("SOLUTION: " + pot.name + " (Priority %d)" %(pot.priority) + " from Room %d" %(pot.room_number) + " lines up with " + entry.name + " (Priority %d)" %(entry.priority) + " from Room %d" %(entry.room_number) + " with offset: " + hex(pot.address - entry.address))
                                                           
                                                            if (pot.address - entry.address) == 0x160:
                                                                angle_solution_count += 1
                                                                print("ANGLE SOLUTION FOUND (CHEST)!!!!!!!!!!!")
                                                            elif (pot.address - entry.address) == 0x1F0:
                                                                position_solution_count += 1
                                                                print("Z POSITION SOLUTION FOUND (CHEST)!!!!!!!!!!!")
                               
                                                            soln_found = True
                                                           
                                                    if soln_found is True:
                                                        total_action_list = action_list + action_list_transition + action_list001
                                                       
                                                        # the "a" argument is important so we don't overwrite previous solutions
                                                        with open(filename, "a") as file:
                                                           
                                                            for action in total_action_list:
                                                               
                                                                file.write(action + "\n")
                                                            file.write("-----\n")
                                   
 
 
 
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
                                                           
                   
                                         
                                                           
                                                           
                                                           
                                                           
"""
 
  Before proceeding, we should define all of the transitions we plan on passing through
 
  Since "Beneath the Graveyard" is relatively simple and I currently only want to consider
  passing through a single plane, I will just define Plane_1 to be the plane shared between
  Room0 and Room1
 
  This loading plane happens the be the second element in Room0_queue, so I will define it based on that
 
"""
 
Oceanside_Plane_0 = Oceanside_Room3_queue[0]
 
 
 
 
 
"""
 
   Grabbable_dict is a dictionary of the grabbable actors (such as pots) that
   we want to attempt to use for superslide SRM where the keys are the grabbable
   actors and the values are lists with 3-bit strings where each bit means:
       
       100 : Possible to enter Plane with both Bomb and Smoke loaded
       010 : Possible to enter Plane with Smoke loaded, but no Bomb loaded
       001 : Possible to enter Plane with no Smoke loaded
   
   and Transitions, where the transitions are the ones you can superslide through
   
   
"""
 
Oceanside_Grabbable_dict = {
        Oceanside_Room3_queue[6] : ['010', Oceanside_Plane_0],
        Oceanside_Room3_queue[7] : ['010', Oceanside_Plane_0]
        }                                                        
                                                           
 
Hardcoded_Allocation_List_0 = [
        'Fish',
        'Fish',
        'Bugs',
        'Bugs',
        'Smoke',
        'Chu',
        'Chu',
        'Chu',
        'Arrow',
        'Arrow',
        'Arrow',
        'Arrow',
        'Arrow',
        'Bomb',
        'Bomb',
        'Bomb',
        'Zora Fins',
        'Hookshot',
        'Charged Spin Attack'
        ]                                                          
 
Hardcoded_Allocation_List_2 = [
        'Smoke',
        'Arrow',
        'Arrow',
        'Arrow',
        'Arrow',
        'Arrow',
        'Bomb',
        'Bomb',
        'Bomb',
        'Hookshot',
        'Charged Spin Attack'
        ]
 
Hardcoded_Allocation_List_2_G = [
        'Gold Skulltula'
        'Smoke',
        'Arrow',
        'Arrow',
        'Arrow',
        'Arrow',
        'Arrow',
        'Bomb',
        'Bomb',
        'Bomb',
        'Hookshot',
        'Charged Spin Attack'
        ]
 
Hardcoded_Allocation_List_3 = [
        'Bomb',
        'Bomb',
        'Bomb',
        'Hookshot',
        'Charged Spin Attack'
        ]
 
Hardcoded_Allocation_List_4 = [
        'Arrow',
        'Arrow',
        'Arrow',
        'Arrow',
        'Arrow',
        'Bomb',
        'Bomb',
        'Bomb',
        'Hookshot',
        'Charged Spin Attack'
        ]
 
 
 
 
 
Allocation_List_Dict_Oceanside_0 = {
        3 : Hardcoded_Allocation_List_2_G,
        4 : Hardcoded_Allocation_List_2
        }
 
 
save_path = "C:\\Users\\xyzabc\\Documents\\Bizhawk RAM Watch\\scripts\\"
name_of_file = "ocean1"
complete_name = save_path + name_of_file + ".txt"  
 
Heap = [Node(0x40B140, node_size), Node(0x5FFFFF, node_size)]
 
##### OCEANSIDE
Randomized_Solver(Oceanside_Room3, Oceanside_Room_List, 5, Allocation_List_Dict_Oceanside_0, Oceanside_Grabbable_dict, Overlay_dict, complete_name, [0x160, 0x1F0], Heap)
 
 
##### BENEATH THE GRAVEYARD
#Randomized_Solver(Room0, Room_List, 3, Hardcoded_Allocation_List_3, Grabbable_dict, Overlay_dict, complete_name, [0x160, 0x1F0], Heap)
 
"""
 
SOME ASSUMPTIONS ABOUT THIS SCRIPT:
   
   - THE SOLVER AUTOMATICALLY CLEARS ALL BAD BATS AT THE START
   
   - WE DO NOT DEALLOCATE WEBS OR GOLD SKULLTULAS IN OCEANSIDE BECAUSE WE WANT
   A SETUP THAT DOES NOT NEED SONG OF TIME STORAGE TO DO REPEATEDLY. EVEN IF IT
   ALLOWED DEALLOCATIONG GOLD SKULLTULAS, IT DOES NOT ACCOUNT FOR THE TOKENS AND
   IT ASSUMES DEALLOCATING A GOLD SKULLTULA IS EQUIVALENT TO PICKING UP ITS TOKEN
   
   - WE ASSUME THAT WE ALWAYS PERFORM THE DEALLOCATION STEPS BEFORE THE ALLOCATION
   STEPS BECAUSE IT IS EASIER TO DEAL WITH SOLUTIONS WITH THIS QUALITY
   
   - THIS SCRIPT HARDCODES HOW WE DEALLOCATE THE 01E7 BONK ACTORS FOR THE OCEANSIDE
   ROOM 3 TABLE
   
   - ALLOCATING GOLD SKULLTULAS IS SPECIFIC TO ROOM 3 OF OCEANSIDE (SHOOTING THE
   PAINTING ALLOCATES A GOLD SKULLTULA)
   
   TODO: (DEKU PALACE CONTEXT) WANT A WAY TO ASSERT THAT A POT NEEDS
   TO BREAK BEFORE PALACE SUPERSLIDE FOR ONE OF THE POTS (I THINK; NEEDS TESTING)
   
   
 
 
"""
