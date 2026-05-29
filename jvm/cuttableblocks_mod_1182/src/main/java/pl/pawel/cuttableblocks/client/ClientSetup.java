package pl.pawel.cuttableblocks.client;

import net.minecraft.client.renderer.blockentity.BlockEntityRenderers;
import net.minecraft.client.resources.model.BakedModel;
import net.minecraft.client.resources.model.ModelResourceLocation;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.properties.AttachFace;
import net.minecraft.world.level.block.state.properties.BedPart;
import net.minecraft.world.level.block.state.properties.DoubleBlockHalf;
import net.minecraft.world.level.block.state.properties.Half;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.ModelBakeEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;
import pl.pawel.cuttableblocks.CuttableBlocksMod;
import pl.pawel.cuttableblocks.client.model.*;
import pl.pawel.cuttableblocks.registry.ModBlockEntities;
import pl.pawel.cuttableblocks.registry.ModBlocks;
import pl.pawel.cuttableblocks.world.*;

import java.util.Map;
import java.util.function.Function;

/**
 * Client-side setup: replaces baked models for Carpenter blocks and registers BER for Cuttable.
 */
@Mod.EventBusSubscriber(modid = CuttableBlocksMod.MODID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.MOD)
public class ClientSetup {

    @SubscribeEvent
    public static void onClientSetup(FMLClientSetupEvent event) {
        event.enqueueWork(() -> {
            // Only cuttable blocks still use BER (arbitrary plane cuts cannot be expressed as BakedModel)
            BlockEntityRenderers.register(
                ModBlockEntities.CUTTABLE.get(),
                CuttableBlockEntityRenderer::new
            );
        });
    }

    @SubscribeEvent
    public static void onModelBake(ModelBakeEvent event) {
        // --- Custom-generated geometry ---
        replaceModel(ModBlocks.CARPENTER_SLOPE.getId(), event, CarpenterSlopeBakedModel::new);
        replaceModel(ModBlocks.CARPENTER_BLOCK.getId(), event, CarpenterBlockBakedModel::new);
        replaceModel(ModBlocks.COLLAPSIBLE_BLOCK.getId(), event, CarpenterCollapsibleBakedModel::new);
        replaceModel(ModBlocks.CARPENTER_BARRIER.getId(), event, CarpenterBarrierBakedModel::new);

        // --- Vanilla-retextured blocks (geometry copied, texture replaced with cover) ---

        // Stairs
        replaceModel(ModBlocks.CARPENTER_STAIRS.getId(), event, d ->
            new VanillaRetextureBakedModel(d, s -> Blocks.OAK_STAIRS.defaultBlockState()
                .setValue(net.minecraft.world.level.block.StairBlock.FACING, s.getValue(CarpenterStairsBlock.FACING))
                .setValue(net.minecraft.world.level.block.StairBlock.HALF, s.getValue(CarpenterStairsBlock.HALF))
                .setValue(net.minecraft.world.level.block.StairBlock.SHAPE, s.getValue(CarpenterStairsBlock.SHAPE)))
        );

        // Door
        replaceModel(ModBlocks.CARPENTER_DOOR.getId(), event, d ->
            new VanillaRetextureBakedModel(d, s -> {
                Half half = s.getValue(CarpenterDoorBlock.HALF);
                DoubleBlockHalf vanillaHalf = (half == Half.TOP) ? DoubleBlockHalf.UPPER : DoubleBlockHalf.LOWER;
                return Blocks.OAK_DOOR.defaultBlockState()
                    .setValue(net.minecraft.world.level.block.DoorBlock.FACING, s.getValue(CarpenterDoorBlock.FACING))
                    .setValue(net.minecraft.world.level.block.DoorBlock.HALF, vanillaHalf)
                    .setValue(net.minecraft.world.level.block.DoorBlock.HINGE, s.getValue(CarpenterDoorBlock.HINGE))
                    .setValue(net.minecraft.world.level.block.DoorBlock.OPEN, s.getValue(CarpenterDoorBlock.OPEN));
            })
        );

        // Hatch / Trapdoor
        replaceModel(ModBlocks.CARPENTER_HATCH.getId(), event, d ->
            new VanillaRetextureBakedModel(d, s -> Blocks.OAK_TRAPDOOR.defaultBlockState()
                .setValue(net.minecraft.world.level.block.TrapDoorBlock.FACING, s.getValue(CarpenterHatchBlock.FACING))
                .setValue(net.minecraft.world.level.block.TrapDoorBlock.HALF, s.getValue(CarpenterHatchBlock.HALF))
                .setValue(net.minecraft.world.level.block.TrapDoorBlock.OPEN, s.getValue(CarpenterHatchBlock.OPEN)))
        );

        // Gate / Fence gate
        replaceModel(ModBlocks.CARPENTER_GATE.getId(), event, d ->
            new VanillaRetextureBakedModel(d, s -> Blocks.OAK_FENCE_GATE.defaultBlockState()
                .setValue(net.minecraft.world.level.block.FenceGateBlock.FACING, s.getValue(CarpenterGateBlock.FACING))
                .setValue(net.minecraft.world.level.block.FenceGateBlock.OPEN, s.getValue(CarpenterGateBlock.OPEN)))
        );

        // Lever
        replaceModel(ModBlocks.CARPENTER_LEVER.getId(), event, d ->
            new VanillaRetextureBakedModel(d, s -> {
                Direction facing = s.getValue(CarpenterLeverBlock.FACING);
                if (facing.getAxis() == Direction.Axis.Y) {
                    facing = Direction.NORTH;
                }
                return Blocks.LEVER.defaultBlockState()
                    .setValue(net.minecraft.world.level.block.LeverBlock.FACE, s.getValue(CarpenterLeverBlock.FACE))
                    .setValue(net.minecraft.world.level.block.LeverBlock.FACING, facing)
                    .setValue(net.minecraft.world.level.block.LeverBlock.POWERED, s.getValue(CarpenterLeverBlock.POWERED));
            })
        );

        // Button
        replaceModel(ModBlocks.CARPENTER_BUTTON.getId(), event, d ->
            new VanillaRetextureBakedModel(d, s -> {
                Direction facing = s.getValue(CarpenterButtonBlock.FACING);
                if (facing.getAxis() == Direction.Axis.Y) {
                    facing = Direction.NORTH;
                }
                return Blocks.OAK_BUTTON.defaultBlockState()
                    .setValue(net.minecraft.world.level.block.ButtonBlock.FACE, s.getValue(CarpenterButtonBlock.FACE))
                    .setValue(net.minecraft.world.level.block.ButtonBlock.FACING, facing)
                    .setValue(net.minecraft.world.level.block.ButtonBlock.POWERED, s.getValue(CarpenterButtonBlock.POWERED));
            })
        );

        // Pressure plate
        replaceModel(ModBlocks.CARPENTER_PRESSURE_PLATE.getId(), event, d ->
            new VanillaRetextureBakedModel(d, s -> Blocks.OAK_PRESSURE_PLATE.defaultBlockState()
                .setValue(net.minecraft.world.level.block.PressurePlateBlock.POWERED, s.getValue(CarpenterPressurePlateBlock.POWERED)))
        );

        // Torch
        replaceModel(ModBlocks.CARPENTER_TORCH.getId(), event, d ->
            new VanillaRetextureBakedModel(d, s -> {
                Direction facing = s.getValue(CarpenterTorchBlock.FACING);
                if (facing == Direction.UP) {
                    return Blocks.TORCH.defaultBlockState();
                } else if (facing.getAxis().isHorizontal()) {
                    return Blocks.WALL_TORCH.defaultBlockState()
                        .setValue(net.minecraft.world.level.block.WallTorchBlock.FACING, facing);
                } else {
                    return Blocks.TORCH.defaultBlockState();
                }
            })
        );

        // Bed
        replaceModel(ModBlocks.CARPENTER_BED.getId(), event, d ->
            new VanillaRetextureBakedModel(d, s -> Blocks.WHITE_BED.defaultBlockState()
                .setValue(net.minecraft.world.level.block.BedBlock.FACING, s.getValue(CarpenterBedBlock.FACING))
                .setValue(net.minecraft.world.level.block.BedBlock.PART, s.getValue(CarpenterBedBlock.PART))
                .setValue(net.minecraft.world.level.block.BedBlock.OCCUPIED, s.getValue(CarpenterBedBlock.OCCUPIED)))
        );

        // Ladder
        replaceModel(ModBlocks.CARPENTER_LADDER.getId(), event, d ->
            new VanillaRetextureBakedModel(d, s -> Blocks.LADDER.defaultBlockState()
                .setValue(net.minecraft.world.level.block.LadderBlock.FACING, s.getValue(CarpenterLadderBlock.FACING)))
        );

        // Daylight sensor
        replaceModel(ModBlocks.CARPENTER_DAYLIGHT_SENSOR.getId(), event, d ->
            new VanillaRetextureBakedModel(d, s -> Blocks.DAYLIGHT_DETECTOR.defaultBlockState()
                .setValue(net.minecraft.world.level.block.DaylightDetectorBlock.INVERTED, s.getValue(CarpenterDaylightSensorBlock.INVERTED)))
        );

        // Flower pot
        replaceModel(ModBlocks.CARPENTER_FLOWER_POT.getId(), event, d ->
            new VanillaRetextureBakedModel(d, s -> Blocks.FLOWER_POT.defaultBlockState())
        );

        // Safe -> chest facing north (no facing in our blockstate)
        replaceModel(ModBlocks.CARPENTER_SAFE.getId(), event, d ->
            new VanillaRetextureBakedModel(d, s -> Blocks.CHEST.defaultBlockState()
                .setValue(net.minecraft.world.level.block.ChestBlock.FACING, Direction.NORTH))
        );

        // Garage door -> lower door as fallback
        replaceModel(ModBlocks.CARPENTER_GARAGE_DOOR.getId(), event, d ->
            new VanillaRetextureBakedModel(d, s -> Blocks.OAK_DOOR.defaultBlockState()
                .setValue(net.minecraft.world.level.block.DoorBlock.FACING, s.getValue(CarpenterGarageDoorBlock.FACING))
                .setValue(net.minecraft.world.level.block.DoorBlock.HALF, DoubleBlockHalf.LOWER)
                .setValue(net.minecraft.world.level.block.DoorBlock.OPEN, false))
        );
    }

    private static void replaceModel(ResourceLocation blockId, ModelBakeEvent event, Function<BakedModel, BakedModel> factory) {
        Map<ResourceLocation, BakedModel> registry = event.getModelRegistry();
        ModelResourceLocation blockLocation = new ModelResourceLocation(blockId, "");
        BakedModel oldBlock = registry.get(blockLocation);
        if (oldBlock != null) {
            registry.put(blockLocation, factory.apply(oldBlock));
        }
        ModelResourceLocation itemLocation = new ModelResourceLocation(blockId, "inventory");
        BakedModel oldItem = registry.get(itemLocation);
        if (oldItem != null) {
            registry.put(itemLocation, factory.apply(oldItem));
        }
    }
}
