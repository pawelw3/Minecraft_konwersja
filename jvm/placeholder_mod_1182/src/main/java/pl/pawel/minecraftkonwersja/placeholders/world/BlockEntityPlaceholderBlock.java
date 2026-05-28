package pl.pawel.minecraftkonwersja.placeholders.world;

import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.TextComponent;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.jetbrains.annotations.Nullable;

public class BlockEntityPlaceholderBlock extends BaseEntityBlock {
    private static final VoxelShape SHAPE = box(6.0D, 0.0D, 6.0D, 10.0D, 12.0D, 10.0D);
    private static final int CHAT_LINE_LIMIT = 240;

    public BlockEntityPlaceholderBlock(Properties properties) {
        super(properties);
    }

    @Override
    public VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return SHAPE;
    }

    @Override
    public VoxelShape getCollisionShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return Shapes.empty();
    }

    @Override
    public RenderShape getRenderShape(BlockState state) {
        return RenderShape.MODEL;
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new BlockEntityPlaceholderBlockEntity(pos, state);
    }

    @Override
    public InteractionResult use(
        BlockState state,
        Level level,
        BlockPos pos,
        Player player,
        InteractionHand hand,
        BlockHitResult hit
    ) {
        if (level.isClientSide) {
            return InteractionResult.SUCCESS;
        }

        BlockEntity blockEntity = level.getBlockEntity(pos);
        if (!(blockEntity instanceof BlockEntityPlaceholderBlockEntity placeholder)) {
            return InteractionResult.PASS;
        }

        sendSummary(player, placeholder, pos);
        if (player.isShiftKeyDown()) {
            sendPaged(player, placeholder.originalNbtAsString(), ChatFormatting.GRAY);
        } else {
            String preview = placeholder.originalNbtPreview(190);
            player.displayClientMessage(new TextComponent("NBT: " + preview).withStyle(ChatFormatting.GRAY), false);
        }
        return InteractionResult.CONSUME;
    }

    private static void sendSummary(Player player, BlockEntityPlaceholderBlockEntity placeholder, BlockPos pos) {
        player.displayClientMessage(new TextComponent("Conversion placeholder").withStyle(ChatFormatting.GOLD), false);
        player.displayClientMessage(new TextComponent("mod=" + placeholder.getSourceMod()
            + " block=" + placeholder.getSourceBlockId()
            + " te=" + placeholder.getSourceTeId()).withStyle(ChatFormatting.YELLOW), false);
        player.displayClientMessage(new TextComponent("metadata=" + placeholder.getSourceMetadata()
            + " source_pos=" + placeholder.getSourcePosString()
            + " current_pos=[" + pos.getX() + "," + pos.getY() + "," + pos.getZ() + "]").withStyle(ChatFormatting.AQUA), false);
        player.displayClientMessage(new TextComponent("reason=" + placeholder.getConversionReason()
            + " stage=" + placeholder.getConversionStage()).withStyle(ChatFormatting.WHITE), false);
    }

    private static void sendPaged(Player player, String text, ChatFormatting formatting) {
        if (text.isEmpty()) {
            player.displayClientMessage(new TextComponent("NBT: {}").withStyle(formatting), false);
            return;
        }
        int page = 1;
        for (int start = 0; start < text.length(); start += CHAT_LINE_LIMIT) {
            int end = Math.min(text.length(), start + CHAT_LINE_LIMIT);
            player.displayClientMessage(new TextComponent("NBT[" + page + "]: " + text.substring(start, end)).withStyle(formatting), false);
            page++;
            if (page > 12) {
                player.displayClientMessage(new TextComponent("NBT output truncated after 12 chat lines").withStyle(ChatFormatting.DARK_GRAY), false);
                break;
            }
        }
    }
}
