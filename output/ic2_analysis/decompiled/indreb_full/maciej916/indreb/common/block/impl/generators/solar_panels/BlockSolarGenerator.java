package com.maciej916.indreb.common.block.impl.generators.solar_panels;

import com.maciej916.indreb.common.block.BlockElectricMachine;
import com.maciej916.indreb.common.enums.EnumLang;
import com.maciej916.indreb.common.interfaces.block.IHasContainer;
import com.maciej916.indreb.common.interfaces.block.IStateActive;
import com.maciej916.indreb.common.tier.SolarGeneratorTier;
import com.maciej916.indreb.common.util.TextComponentUtil;
import java.util.List;
import javax.annotation.Nullable;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.network.chat.TranslatableComponent;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

public class BlockSolarGenerator extends BlockElectricMachine implements IHasContainer, IStateActive {
   private final SolarGeneratorTier solarTier;
   protected final VoxelShape SHAPE;

   public BlockSolarGenerator(SolarGeneratorTier tier) {
      super(tier.getEnergyTier(), 0, 0);
      this.SHAPE = Block.m_49796_(0.0, 0.0, 0.0, 16.0, tier.getHeight(), 16.0);
      this.solarTier = tier;
   }

   @Nullable
   public BlockEntity m_142194_(BlockPos pos, BlockState state) {
      return new BlockEntitySolarGenerator(pos, state);
   }

   public ContainerSolarGenerator getContainer(int windowId, Level level, BlockPos pos, Inventory playerInventory, Player playerEntity) {
      return new ContainerSolarGenerator(windowId, level, pos, playerInventory, playerEntity);
   }

   public VoxelShape m_5940_(BlockState pState, BlockGetter pLevel, BlockPos pPos, CollisionContext pContext) {
      return this.SHAPE;
   }

   public VoxelShape m_5939_(BlockState pState, BlockGetter pLevel, BlockPos pPos, CollisionContext pContext) {
      return this.SHAPE;
   }

   public void m_5871_(ItemStack pStack, @Nullable BlockGetter pLevel, List<Component> pTooltip, TooltipFlag pFlag) {
      super.m_5871_(pStack, pLevel, pTooltip, pFlag);
      pTooltip.add(
         TextComponentUtil.build(
            new MutableComponent[]{
               new TranslatableComponent(EnumLang.GENERATE.getTranslationKey()).m_130940_(ChatFormatting.GRAY),
               new TranslatableComponent(
                     EnumLang.POWER_TICK.getTranslationKey(), new Object[]{TextComponentUtil.getFormattedEnergyUnit((float)this.solarTier.getDayGenerate())}
                  )
                  .m_130940_(this.getEnergyTier().getColor())
            }
         )
      );
   }

   public SolarGeneratorTier getSolarGeneratorTier() {
      return this.solarTier;
   }
}
