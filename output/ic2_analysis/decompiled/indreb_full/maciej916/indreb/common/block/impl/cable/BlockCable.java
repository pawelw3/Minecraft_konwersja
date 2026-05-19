package com.maciej916.indreb.common.block.impl.cable;

import com.maciej916.indreb.common.block.VoxelBlock;
import com.maciej916.indreb.common.enums.EnumLang;
import com.maciej916.indreb.common.registries.ModCapabilities;
import com.maciej916.indreb.common.tier.CableTier;
import com.maciej916.indreb.common.util.BlockStateHelper;
import com.maciej916.indreb.common.util.CapabilityUtil;
import com.maciej916.indreb.common.util.Constants;
import com.maciej916.indreb.common.util.TextComponentUtil;
import com.maciej916.indreb.common.util.wrench.WrenchHelper;
import java.util.List;
import javax.annotation.Nullable;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.network.chat.TranslatableComponent;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Explosion;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.SimpleWaterloggedBlock;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.Property;
import net.minecraft.world.level.material.FluidState;
import net.minecraft.world.level.material.Fluids;

public class BlockCable extends VoxelBlock implements SimpleWaterloggedBlock, EntityBlock {
   private final CableTier cableTier;

   public BlockCable(float apothem, CableTier tier) {
      super(tier.getProperties(), apothem);
      this.cableTier = tier;
      WrenchHelper.registerAction(this).add(WrenchHelper.dropAction());
   }

   @Nullable
   public BlockEntity m_142194_(BlockPos pos, BlockState state) {
      return new BlockEntityCable(pos, state);
   }

   public void m_5871_(ItemStack pStack, @Nullable BlockGetter pLevel, List<Component> pTooltip, TooltipFlag pFlag) {
      pTooltip.add(
         TextComponentUtil.build(
            new MutableComponent[]{
               new TranslatableComponent(EnumLang.POWER_TIER.getTranslationKey()).m_130940_(ChatFormatting.GRAY),
               new TranslatableComponent(this.cableTier.getEnergyTier().getLang().getTranslationKey()).m_130940_(this.cableTier.getEnergyTier().getColor())
            }
         )
      );
      pTooltip.add(
         TextComponentUtil.build(
            new MutableComponent[]{
               new TranslatableComponent(EnumLang.TRANSFER.getTranslationKey()).m_130940_(ChatFormatting.GRAY),
               new TranslatableComponent(
                     EnumLang.POWER_TICK.getTranslationKey(),
                     new Object[]{TextComponentUtil.getFormattedEnergyUnit((float)this.cableTier.getEnergyTier().getBasicTransfer())}
                  )
                  .m_130940_(this.cableTier.getEnergyTier().getColor())
            }
         )
      );
      if (!this.cableTier.isInsulated()) {
         pTooltip.add(
            TextComponentUtil.build(
               new MutableComponent[]{new TranslatableComponent(EnumLang.CABLE_UNISOLATED.getTranslationKey()).m_130940_(ChatFormatting.RED)}
            )
         );
      }
   }

   public CableTier getCableTier() {
      return this.cableTier;
   }

   protected boolean canConnect(LevelAccessor world, BlockPos pos, Direction direction) {
      BlockEntity be = world.m_7702_(pos);
      BlockState state = world.m_8055_(pos);
      return state.m_60734_() instanceof BlockCable bc
         ? bc.getCableTier().getEnergyTier() == this.cableTier.getEnergyTier()
         : (Boolean)CapabilityUtil.getCapabilityHelper(be, ModCapabilities.ENERGY, direction)
            .getIfPresentElse(e -> e.canExtractEnergy(direction.m_122424_()) || e.canReceiveEnergy(direction.m_122424_()), false);
   }

   public void m_6807_(BlockState state, Level level, BlockPos pos, BlockState oldState, boolean isMoving) {
      if (!level.m_5776_()) {
         if (oldState.m_60734_() != state.m_60734_()) {
            CapabilityUtil.getCapabilityHelper(level, ModCapabilities.ENERGY_CORE)
               .ifPresent(e -> e.getNetworks().onPlaced(pos, state, this.cableTier.getEnergyTier()));
         }

         super.m_6807_(state, level, pos, oldState, isMoving);
      }
   }

   public void m_6810_(BlockState state, Level pLevel, BlockPos pos, BlockState newState, boolean pIsMoving) {
      if (!pLevel.m_5776_()) {
         if (newState.m_60734_() != state.m_60734_()) {
            CapabilityUtil.getCapabilityHelper(pLevel, ModCapabilities.ENERGY_CORE).ifPresent(e -> e.getNetworks().onRemove(pos));
         }

         super.m_6810_(state, pLevel, pos, newState, pIsMoving);
      }
   }

   public void m_6861_(BlockState pState, Level pLevel, BlockPos pPos, Block pBlock, BlockPos pFromPos, boolean pIsMoving) {
      if (!pLevel.m_5776_()) {
         CapabilityUtil.getCapabilityHelper(pLevel, ModCapabilities.ENERGY_CORE).ifPresent(e -> e.getNetworks().neighborChanged(pPos, pFromPos));
         super.m_6861_(pState, pLevel, pPos, pBlock, pFromPos, pIsMoving);
      }
   }

   @Deprecated
   public FluidState m_5888_(BlockState state) {
      return state.m_61143_(BlockStateHelper.waterlogged) ? Fluids.f_76193_.m_76068_(false) : super.m_5888_(state);
   }

   @Deprecated
   public BlockState m_7417_(BlockState state, Direction facing, BlockState facingState, LevelAccessor level, BlockPos pos, BlockPos facingPos) {
      if ((Boolean)state.m_61143_(BlockStateHelper.waterlogged)) {
         level.m_186469_(pos, Fluids.f_76193_, Fluids.f_76193_.m_6718_(level));
      }

      for (Direction direction : Constants.DIRECTIONS) {
         boolean valid = this.canConnect(level, pos.m_142300_(direction), direction);
         state = (BlockState)state.m_61124_((Property)FACING_TO_PROPERTY_MAP.get(direction), valid);
      }

      return state;
   }

   public void onBlockExploded(BlockState state, Level world, BlockPos pos, Explosion explosion) {
      if (!world.m_5776_()) {
         CapabilityUtil.getCapabilityHelper(world, ModCapabilities.ENERGY_CORE).ifPresent(e -> e.getNetworks().onRemove(pos));
         super.onBlockExploded(state, world, pos, explosion);
      }
   }
}
