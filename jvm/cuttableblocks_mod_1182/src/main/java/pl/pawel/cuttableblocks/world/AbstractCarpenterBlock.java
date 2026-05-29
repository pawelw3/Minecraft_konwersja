package pl.pawel.cuttableblocks.world;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.DyeItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.minecraftforge.registries.ForgeRegistries;
import org.jetbrains.annotations.Nullable;

/**
 * Base class for all 18 carpenter_* block types.
 *
 * Handles:
 * - BlockEntity creation (all carpenter blocks share CarpenterBlockEntity)
 * - Cover application (BlockItem), dye application (DyeItem), illuminator (Glowstone)
 * - Pass-through for tools (Hammer, CuttingTool)
 *
 * Per-type geometry, blockstates, and collision are implemented in subclasses.
 */
public abstract class AbstractCarpenterBlock extends Block implements EntityBlock {

    public AbstractCarpenterBlock(Properties properties) {
        super(properties);
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new CarpenterBlockEntity(pos, state);
    }

    @Override
    public RenderShape getRenderShape(BlockState state) {
        return RenderShape.MODEL;
    }

    @Override
    public InteractionResult use(BlockState state, Level level, BlockPos pos,
                                 Player player, InteractionHand hand, BlockHitResult hit) {
        ItemStack held = player.getItemInHand(hand);
        BlockEntity be = level.getBlockEntity(pos);
        if (!(be instanceof CarpenterBlockEntity cbe)) {
            return InteractionResult.PASS;
        }

        // 1. Tools must get PASS so their Item#useOn fires
        if (!held.isEmpty()) {
            if (held.getItem() instanceof pl.pawel.cuttableblocks.items.CarpenterHammer
             || held.getItem() instanceof pl.pawel.cuttableblocks.items.CuttingTool) {
                return InteractionResult.PASS;
            }
        }

        // 2. Empty hand -> subclass-defined behaviour (default none)
        if (held.isEmpty()) {
            return useEmptyHand(state, level, pos, player, hand, hit);
        }

        // 3. Glowstone dust -> toggle illuminator
        if (held.getItem() == Items.GLOWSTONE_DUST) {
            if (!level.isClientSide) {
                cbe.setIlluminator(!cbe.isIlluminator());
                level.sendBlockUpdated(pos, state, state, Block.UPDATE_NEIGHBORS | Block.UPDATE_CLIENTS);
            }
            return InteractionResult.sidedSuccess(level.isClientSide);
        }

        // 4. Dye -> apply to clicked side
        if (held.getItem() instanceof DyeItem dyeItem) {
            if (!level.isClientSide) {
                Direction side = hit.getDirection();
                String dyeName = dyeItem.getDyeColor().getName();
                cbe.setSideDye(side.get3DDataValue(), dyeName);
                level.sendBlockUpdated(pos, state, state, Block.UPDATE_NEIGHBORS | Block.UPDATE_CLIENTS);
            }
            return InteractionResult.sidedSuccess(level.isClientSide);
        }

        // 5. Block item -> cover (shift = side cover, no-shift = base cover)
        if (held.getItem() instanceof BlockItem blockItem) {
            if (!level.isClientSide) {
                String blockId = ForgeRegistries.BLOCKS.getKey(blockItem.getBlock()).toString();
                if (player.isShiftKeyDown()) {
                    Direction side = hit.getDirection();
                    cbe.setSideCover(side.get3DDataValue(), blockId);
                } else {
                    cbe.setCoverBlock(blockId);
                }
                level.sendBlockUpdated(pos, state, state, Block.UPDATE_NEIGHBORS | Block.UPDATE_CLIENTS);
            }
            return InteractionResult.sidedSuccess(level.isClientSide);
        }

        return InteractionResult.PASS;
    }

    /**
     * Subclasses override this to define empty-hand behaviour (e.g. toggle door open).
     * Default does nothing.
     */
    protected InteractionResult useEmptyHand(BlockState state, Level level, BlockPos pos,
                                             Player player, InteractionHand hand, BlockHitResult hit) {
        return InteractionResult.PASS;
    }

    // --- Collision / Selection shapes (subclasses override) ----------------

    @Override
    public VoxelShape getShape(BlockState state, net.minecraft.world.level.BlockGetter level,
                               BlockPos pos, CollisionContext context) {
        return getCarpenterShape(state);
    }

    @Override
    public VoxelShape getCollisionShape(BlockState state, net.minecraft.world.level.BlockGetter level,
                                        BlockPos pos, CollisionContext context) {
        return getCarpenterShape(state);
    }

    protected VoxelShape getCarpenterShape(BlockState state) {
        return Shapes.block();
    }
}
