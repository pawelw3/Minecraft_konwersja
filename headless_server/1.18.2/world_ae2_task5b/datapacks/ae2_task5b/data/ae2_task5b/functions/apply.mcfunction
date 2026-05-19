say [AE2_TASK5B] applying converted AE2 5A patch
setblock 96 64 96 minecraft:polished_andesite replace
setblock 96 65 96 minecraft:lever[face=floor,facing=east,powered=false] replace
setblock 97 64 96 minecraft:polished_andesite replace
setblock 97 65 96 minecraft:redstone_wire[east=side,north=none,power=0,south=none,west=side] replace
setblock 98 64 96 minecraft:polished_andesite replace
setblock 98 65 96 minecraft:redstone_wire[east=side,north=none,power=0,south=none,west=side] replace
setblock 99 64 96 minecraft:polished_andesite replace
setblock 99 65 96 minecraft:redstone_wire[east=side,north=none,power=0,south=none,west=side] replace
setblock 100 64 96 minecraft:polished_andesite replace
setblock 100 64 100 ae2:fluix_block replace
setblock 100 64 103 ae2:4k_crafting_storage{size_variant:1,formed:true,size_bytes:4096,customName:"CPU storage meta 5"} replace
setblock 100 64 106 minecraft:grindstone replace
setblock 100 64 109 ae2:spatial_io_port{lastRedstoneState:0} replace
setblock 100 65 96 minecraft:command_block[conditional=false,facing=west]{id:"minecraft:command_block",x:100,y:65,z:96,Command:"say AE2_TASK5A_REDSTONE_PASS",CustomName:"{\"text\":\"AE2_5A_ASSERT\"}",TrackOutput:true,auto:false,powered:false,SuccessCount:0} replace
setblock 103 64 100 ae2:fluix_block replace
setblock 103 64 103 ae2:16k_crafting_storage{size_variant:2,formed:true,size_bytes:16384,customName:"CPU storage meta 6"} replace
setblock 103 64 106 ae2:io_port{lastRedstoneState:1,inv:{item0:{id:"ae2:item_storage_cell_1k",Count:1,tag:{storage:{items:[{id:"minecraft:stone",Count:100}],count:100}}}}} replace
setblock 103 64 109 ae2:spatial_pylon replace
setblock 106 64 100 ae2:charger{items:[{id:"ae2:multimaterial",Count:1}],internalCurrentPower:2000} replace
setblock 106 64 103 ae2:64k_crafting_storage{size_variant:3,formed:true,size_bytes:65536,customName:"CPU storage meta 7"} replace
setblock 106 64 106 ae2:inscriber{items:[{id:"ae2:multimaterial",Count:1,tag:{Damage:13}},{id:"ae2:multimaterial",Count:1,tag:{Damage:19}}],progress:20} replace
setblock 106 64 109 ae2:tiny_tnt replace
setblock 109 64 100 ae2:chest{priority:3,inv:{item0:{id:"ae2:item_storage_cell_4k",Count:1,tag:{storage:{items:[{id:"minecraft:diamond",Count:32}],count:32}}}}} replace
setblock 109 64 103 ae2:crafting_unit{core:true,inventory:[{id:"minecraft:iron_ingot",Count:8}]} replace
setblock 109 64 105 ae2:pattern_provider{items:[{id:"ae2:crafting_pattern",Count:1,tag:{inputs:[{id:"minecraft:oak_planks",Count:4},{},{},{},{},{},{},{},{}],result:{id:"minecraft:crafting_table",Count:1},recipeId:"minecraft:unknown",canSubstitute:false,canSubstituteFluids:false},Slot:0},{id:"ae2:processing_pattern",Count:1,tag:{inputs:[{item:"minecraft:iron_ingot",count:1},{item:"minecraft:coal",count:1}],outputs:[{item:"minecraft:steel_ingot",count:1}],can_substitute:true},Slot:1}],priority:25,blockingMode:false} replace
setblock 109 64 106 ae2:interface{priority:25,config:[{Slot:0,id:"minecraft:iron_ingot",Count:1}],items:[{id:"minecraft:chest",Count:16,Slot:3}],fuzzyMode:"IGNORE_ALL"} replace
setblock 109 64 109 ae2:vibration_chamber{internalCurrentPower:0} replace
setblock 112 64 100 ae2:condenser replace
setblock 112 64 103 ae2:crafting_accelerator{core:false} replace
setblock 112 64 106 ae2:light_detector[facing=north] replace
setblock 112 64 109 ae2:wireless_access_point{items:[{id:"ae2:multimaterial",Count:16,tag:{Damage:42}}]} replace
setblock 115 64 100 ae2:controller replace
setblock 115 64 103 ae2:crafting_unit{core:true,inventory:[{id:"minecraft:iron_ingot",Count:8}]} replace
setblock 115 64 106 ae2:molecular_assembler{customName:"Assembler active"} replace
setblock 115 64 109 ae2:quartz_fixture replace
setblock 118 64 100 ae2:crafting_monitor replace
setblock 118 64 103 ae2:crafting_accelerator{core:false} replace
setblock 118 64 106 ae2:quantum_link{singularity:{pair_id:"task5a-quantum"},items:[{id:"ae2:singularity",Count:1}],status:"offline"} replace
setblock 121 64 100 ae2:1k_crafting_storage{size_variant:0,formed:false,size_bytes:1024,customName:"CPU storage meta 0"} replace
setblock 121 64 103 minecraft:lever replace
setblock 121 64 106 ae2:quantum_ring replace
setblock 124 64 100 ae2:4k_crafting_storage{size_variant:1,formed:false,size_bytes:4096,customName:"CPU storage meta 1"} replace
setblock 124 64 103 ae2:dense_energy_cell replace
setblock 124 64 106 ae2:quartz_growth_accelerator replace
setblock 127 64 100 ae2:16k_crafting_storage{size_variant:2,formed:false,size_bytes:16384,customName:"CPU storage meta 2"} replace
setblock 127 64 103 ae2:drive{priority:7,inv:{item0:{id:"ae2:item_storage_cell_1k",Count:1,tag:{storage:{items:[{id:"minecraft:cobblestone",Count:512}],count:512}}},item1:{id:"ae2:item_storage_cell_4k",Count:1,tag:{storage:{items:[{id:"minecraft:iron_ingot",Count:128}],count:128}}},item2:{id:"ae2:item_storage_cell_16k",Count:1,tag:{storage:{items:[{id:"minecraft:gold_ingot",Count:64}],count:64}}},item3:{id:"ae2:item_storage_cell_64k",Count:1,tag:{storage:{items:[{id:"minecraft:diamond",Count:16}],count:16}}},item4:{}}} replace
setblock 127 64 106 ae2:quartz_fixture replace
setblock 130 64 100 ae2:64k_crafting_storage{size_variant:3,formed:false,size_bytes:65536,customName:"CPU storage meta 3"} replace
setblock 130 64 103 ae2:energy_acceptor replace
setblock 130 64 106 ae2:security_station{players:[{name:"pawel",uuid:"legacy-offline",permissions:255}],owner:"pawel"} replace
setblock 133 64 100 ae2:1k_crafting_storage{size_variant:0,formed:true,size_bytes:1024,customName:"CPU storage meta 4"} replace
setblock 133 64 103 ae2:energy_cell replace
setblock 133 64 106 ae2:sky_stone_chest{priority:0,inv:{item0:{id:"minecraft:certus_quartz_crystal",Count:12}}} replace
say [AE2_TASK5B] apply complete
