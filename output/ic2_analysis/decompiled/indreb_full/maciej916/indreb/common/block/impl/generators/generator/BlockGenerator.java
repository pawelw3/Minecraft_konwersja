package com.maciej916.indreb.common.block.impl.generators.generator;

import com.maciej916.indreb.common.block.BlockElectricMachine;
import com.maciej916.indreb.common.config.ServerConfig;
import com.maciej916.indreb.common.enums.EnergyTier;
import com.maciej916.indreb.common.enums.EnumLang;
import com.maciej916.indreb.common.interfaces.block.IHasContainer;
import com.maciej916.indreb.common.interfaces.block.IStateActive;
import com.maciej916.indreb.common.interfaces.block.IStateFacing;
import com.maciej916.indreb.common.util.BlockStateHelper;
import com.maciej916.indreb.common.util.TextComponentUtil;
import java.util.List;
import java.util.Random;
import javax.annotation.Nullable;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.Direction.Axis;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.network.chat.TextComponent;
import net.minecraft.network.chat.TranslatableComponent;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

public class BlockGenerator extends BlockElectricMachine implements IStateFacing, IHasContainer, IStateActive {
   public BlockGenerator() {
      super(EnergyTier.BASIC, 12, 0);
   }

   @Nullable
   public BlockEntity m_142194_(BlockPos pos, BlockState state) {
      return new BlockEntityGenerator(pos, state);
   }

   public ContainerGenerator getContainer(int windowId, Level level, BlockPos pos, Inventory playerInventory, Player playerEntity) {
      return new ContainerGenerator(windowId, level, pos, playerInventory, playerEntity);
   }

   @OnlyIn(Dist.CLIENT)
   public void m_7100_(BlockState stateIn, Level worldIn, BlockPos pos, Random rand) {
      if ((Boolean)stateIn.m_61143_(BlockStateHelper.activeProperty)) {
         double d0 = (double)pos.m_123341_() + 0.5;
         double d1 = (double)pos.m_123342_();
         double d2 = (double)pos.m_123343_() + 0.5;
         Direction direction = this.getDirection(stateIn);
         Axis direction$axis = direction.m_122434_();
         double d3 = 0.52;
         double d4 = rand.nextDouble() * 0.6 - 0.3;
         double d5 = direction$axis == Axis.X ? (double)direction.m_122429_() * d3 : d4;
         double d6 = rand.nextDouble() * 6.0 / 16.0;
         double d7 = direction$axis == Axis.Z ? (double)direction.m_122431_() * d3 : d4;
         worldIn.m_7106_(ParticleTypes.f_123762_, d0 + d5, d1 + d6, d2 + d7, 0.0, 0.0, 0.0);
         worldIn.m_7106_(ParticleTypes.f_123744_, d0 + d5, d1 + d6, d2 + d7, 0.0, 0.0, 0.0);
      }
   }

   public void m_5871_(ItemStack pStack, @Nullable BlockGetter pLevel, List<Component> pTooltip, TooltipFlag pFlag) {
      super.m_5871_(pStack, pLevel, pTooltip, pFlag);
      pTooltip.add(
         TextComponentUtil.build(
            new MutableComponent[]{
               new TranslatableComponent(EnumLang.GENERATE.getTranslationKey()).m_130940_(ChatFormatting.GRAY),
               new TranslatableComponent(
                     EnumLang.POWER_TICK.getTranslationKey(),
                     new Object[]{TextComponentUtil.getFormattedEnergyUnit((float)((Integer)ServerConfig.generator_tick_generate.get()).intValue())}
                  )
                  .m_130940_(this.getEnergyTier().getColor())
            }
         )
      );
      pTooltip.add(
         TextComponentUtil.build(
            new MutableComponent[]{
               new TranslatableComponent(EnumLang.OUTPUT.getTranslationKey()).m_130940_(ChatFormatting.GRAY),
               new TranslatableComponent(
                     EnumLang.POWER_TICK.getTranslationKey(),
                     new Object[]{TextComponentUtil.getFormattedEnergyUnit((float)((Integer)ServerConfig.basic_tier_transfer.get()).intValue())}
                  )
                  .m_130940_(this.getEnergyTier().getColor()),
               new TextComponent(" "),
               new TranslatableComponent(EnumLang.CAPACITY.getTranslationKey()).m_130940_(ChatFormatting.GRAY),
               new TranslatableComponent(
                     EnumLang.POWER.getTranslationKey(),
                     new Object[]{TextComponentUtil.getFormattedEnergyUnit((float)((Integer)ServerConfig.generator_energy_capacity.get()).intValue())}
                  )
                  .m_130940_(this.getEnergyTier().getColor())
            }
         )
      );
   }
}
