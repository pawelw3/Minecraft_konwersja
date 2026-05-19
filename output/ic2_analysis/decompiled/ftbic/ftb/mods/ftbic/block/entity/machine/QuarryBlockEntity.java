package dev.ftb.mods.ftbic.block.entity.machine;

import dev.ftb.mods.ftbic.FTBICConfig;
import dev.ftb.mods.ftbic.block.FTBICBlocks;
import dev.ftb.mods.ftbic.block.FTBICElectricBlocks;
import dev.ftb.mods.ftbic.screen.QuarryMenu;
import dev.ftb.mods.ftbic.util.FTBICUtils;
import java.util.ArrayList;
import java.util.List;
import java.util.function.Predicate;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.material.Fluids;
import net.minecraft.world.level.storage.loot.LootContext.Builder;
import net.minecraft.world.level.storage.loot.parameters.LootContextParams;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;

public class QuarryBlockEntity extends DiggingBaseBlockEntity {
   private static final Predicate<ItemEntity> ITEM_ENTITY_PREDICATE = entity -> true;
   private static final float[] LASER_COLOR = new float[]{1.0F, 0.1F, 0.1F};

   public QuarryBlockEntity(BlockPos pos, BlockState state) {
      super(FTBICElectricBlocks.QUARRY, pos, state);
   }

   @Override
   public void initProperties() {
      super.initProperties();
      this.diggingMineTicks = (Long)FTBICConfig.MACHINES.QUARRY_MINE_TICKS.get();
      this.diggingMoveTicks = (Long)FTBICConfig.MACHINES.QUARRY_MOVE_TICKS.get();
   }

   @Override
   public boolean isValidBlock(BlockState state, BlockPos pos) {
      return state.m_60767_().m_76334_() && state.m_60800_(this.f_58857_, pos) >= 0.0F;
   }

   @Override
   public void digBlock(BlockState state, BlockPos miningPos, double lx, double ly, double lz) {
      BlockEntity minedEntity = state.m_155947_() ? this.f_58857_.m_7702_(miningPos) : null;
      Builder lootContext = new Builder((ServerLevel)this.f_58857_)
         .m_78977_(this.f_58857_.f_46441_)
         .m_78972_(LootContextParams.f_81460_, new Vec3(lx, ly, lz))
         .m_78972_(LootContextParams.f_81463_, new ItemStack(Items.f_42395_))
         .m_78972_(LootContextParams.f_81461_, state)
         .m_78984_(LootContextParams.f_81462_, minedEntity);
      List<ItemStack> list = new ArrayList<>(state.m_60724_(lootContext));
      this.f_58857_.m_7471_(miningPos, false);
      this.f_58857_.m_5898_(null, 2001, miningPos, Block.m_49956_(state));
      AABB aabb = new AABB(lx - 0.7, ly - 0.7, lz - 0.7, lx + 0.7, ly + 2.7, lz + 0.7);

      for (ItemEntity itemEntity : this.f_58857_.m_6443_(ItemEntity.class, aabb, ITEM_ENTITY_PREDICATE)) {
         list.add(itemEntity.m_32055_());
         itemEntity.m_6074_();
      }

      if (!list.isEmpty()) {
         this.ejectOutputItems();

         for (ItemStack stack : list) {
            ItemStack stack1 = this.addOutput(stack);
            if (!stack1.m_41619_()) {
               Block.m_49840_(this.f_58857_, this.f_58858_.m_142300_(this.getFacing(Direction.NORTH)), stack1);
               this.paused = true;
            }
         }

         this.ejectOutputItems();
      }

      for (Direction direction : FTBICUtils.DIRECTIONS) {
         if (direction != Direction.DOWN && this.f_58857_.m_6425_(miningPos.m_142300_(direction)).m_76152_() != Fluids.f_76191_) {
            BlockState replaceState = FTBICConfig.MACHINES.QUARRY_REPLACE_FLUID_EXFLUID.get()
               ? ((Block)FTBICBlocks.EXFLUID.get()).m_49966_()
               : Blocks.f_50016_.m_49966_();
            this.f_58857_.m_7731_(miningPos, replaceState, 2);
            break;
         }
      }
   }

   @Override
   public InteractionResult rightClick(Player player, InteractionHand hand, BlockHitResult hit) {
      if (!this.f_58857_.m_5776_()) {
         if (player.m_6047_()) {
            this.paused = !this.paused;
            this.syncBlock();
         } else {
            this.openMenu((ServerPlayer)player, (id, inventory) -> new QuarryMenu(id, inventory, this));
         }
      }

      return InteractionResult.SUCCESS;
   }

   @Override
   public float[] getLaserColor() {
      return LASER_COLOR;
   }
}
