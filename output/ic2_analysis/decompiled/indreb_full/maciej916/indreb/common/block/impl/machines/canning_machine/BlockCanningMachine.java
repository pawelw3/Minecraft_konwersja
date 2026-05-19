package com.maciej916.indreb.common.block.impl.machines.canning_machine;

import com.maciej916.indreb.common.block.BlockElectricMachine;
import com.maciej916.indreb.common.config.ServerConfig;
import com.maciej916.indreb.common.enums.EnergyTier;
import com.maciej916.indreb.common.enums.EnumLang;
import com.maciej916.indreb.common.interfaces.block.IHasContainer;
import com.maciej916.indreb.common.interfaces.block.IStateActive;
import com.maciej916.indreb.common.interfaces.block.IStateFacing;
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
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;

public class BlockCanningMachine extends BlockElectricMachine implements IStateFacing, IHasContainer, IStateActive {
   public BlockCanningMachine() {
      super(EnergyTier.BASIC, 0, 0);
   }

   public AbstractContainerMenu getContainer(int windowId, Level level, BlockPos pos, Inventory playerInventory, Player playerEntity) {
      return new ContainerCanningMachine(windowId, level, pos, playerInventory, playerEntity);
   }

   @Nullable
   public BlockEntity m_142194_(BlockPos pos, BlockState state) {
      return new BlockEntityCanningMachine(pos, state);
   }

   public void m_5871_(ItemStack pStack, @Nullable BlockGetter pLevel, List<Component> pTooltip, TooltipFlag pFlag) {
      super.m_5871_(pStack, pLevel, pTooltip, pFlag);
      pTooltip.add(
         TextComponentUtil.build(
            new MutableComponent[]{
               new TranslatableComponent(EnumLang.ACCEPT.getTranslationKey()).m_130940_(ChatFormatting.GRAY),
               new TranslatableComponent(
                     EnumLang.POWER_TICK.getTranslationKey(),
                     new Object[]{TextComponentUtil.getFormattedEnergyUnit((float)((Integer)ServerConfig.basic_tier_transfer.get()).intValue())}
                  )
                  .m_130940_(EnergyTier.BASIC.getColor())
            }
         )
      );
      pTooltip.add(
         TextComponentUtil.build(
            new MutableComponent[]{
               new TranslatableComponent(EnumLang.CAPACITY.getTranslationKey()).m_130940_(ChatFormatting.GRAY),
               new TranslatableComponent(
                     EnumLang.POWER.getTranslationKey(),
                     new Object[]{TextComponentUtil.getFormattedEnergyUnit((float)((Integer)ServerConfig.extruder_energy_capacity.get()).intValue())}
                  )
                  .m_130940_(EnergyTier.BASIC.getColor())
            }
         )
      );
   }
}
