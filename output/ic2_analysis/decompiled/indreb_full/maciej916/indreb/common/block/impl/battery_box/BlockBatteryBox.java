package com.maciej916.indreb.common.block.impl.battery_box;

import com.maciej916.indreb.common.block.IndRebEntityBlock;
import com.maciej916.indreb.common.enums.EnergyTier;
import com.maciej916.indreb.common.enums.EnumLang;
import com.maciej916.indreb.common.interfaces.block.IElectricMachine;
import com.maciej916.indreb.common.interfaces.block.IHasContainer;
import com.maciej916.indreb.common.interfaces.block.IStateFacing;
import com.maciej916.indreb.common.tier.BatteryBoxTier;
import com.maciej916.indreb.common.util.BlockStateHelper;
import com.maciej916.indreb.common.util.TextComponentUtil;
import com.maciej916.indreb.common.util.wrench.WrenchHelper;
import java.util.List;
import javax.annotation.Nonnull;
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
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.BlockBehaviour.Properties;
import net.minecraft.world.level.block.state.properties.DirectionProperty;

public class BlockBatteryBox extends IndRebEntityBlock implements IStateFacing, IHasContainer, IElectricMachine {
   private final BatteryBoxTier batteryBoxTier;

   public BlockBatteryBox(BatteryBoxTier batteryBoxTier, Properties properties) {
      super(properties);
      this.batteryBoxTier = batteryBoxTier;
      WrenchHelper.registerAction(this).add(WrenchHelper.rotationHitAction()).add(WrenchHelper.dropAction());
   }

   public BatteryBoxTier getBatteryBoxTier() {
      return this.batteryBoxTier;
   }

   @Nonnull
   public DirectionProperty getFacingProperty() {
      return BlockStateHelper.facingProperty;
   }

   @Nullable
   public BlockEntity m_142194_(BlockPos pos, BlockState state) {
      return new BlockEntityBatteryBox(pos, state);
   }

   public ContainerBatteryBox getContainer(int windowId, Level level, BlockPos pos, Inventory playerInventory, Player playerEntity) {
      return new ContainerBatteryBox(windowId, level, pos, playerInventory, playerEntity);
   }

   public void m_5871_(ItemStack pStack, @Nullable BlockGetter pLevel, List<Component> pTooltip, TooltipFlag pFlag) {
      pTooltip.add(
         TextComponentUtil.build(
            new MutableComponent[]{
               new TranslatableComponent(EnumLang.POWER_TIER.getTranslationKey()).m_130940_(ChatFormatting.GRAY),
               new TranslatableComponent(this.batteryBoxTier.getEnergyTier().getLang().getTranslationKey())
                  .m_130940_(this.batteryBoxTier.getEnergyTier().getColor())
            }
         )
      );
      pTooltip.add(
         TextComponentUtil.build(
            new MutableComponent[]{
               new TranslatableComponent(EnumLang.TRANSFER.getTranslationKey()).m_130940_(ChatFormatting.GRAY),
               new TranslatableComponent(
                     EnumLang.POWER_TICK.getTranslationKey(),
                     new Object[]{TextComponentUtil.getFormattedEnergyUnit((float)this.batteryBoxTier.getEnergyTier().getBasicTransfer())}
                  )
                  .m_130940_(this.batteryBoxTier.getEnergyTier().getColor())
            }
         )
      );
      pTooltip.add(
         TextComponentUtil.build(
            new MutableComponent[]{
               new TranslatableComponent(EnumLang.CAPACITY.getTranslationKey()).m_130940_(ChatFormatting.GRAY),
               new TranslatableComponent(
                     EnumLang.POWER.getTranslationKey(), new Object[]{TextComponentUtil.getFormattedEnergyUnit((float)this.batteryBoxTier.getEnergyCapacity())}
                  )
                  .m_130940_(this.batteryBoxTier.getEnergyTier().getColor())
            }
         )
      );
   }

   public EnergyTier getEnergyTier() {
      return this.batteryBoxTier.getEnergyTier();
   }
}
