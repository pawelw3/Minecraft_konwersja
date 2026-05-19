package com.maciej916.indreb.common.block.impl.charge_pad;

import com.maciej916.indreb.common.energy.impl.BasicEnergyStorage;
import com.maciej916.indreb.common.enums.EnumLang;
import com.maciej916.indreb.common.screen.BetterScreen;
import com.maciej916.indreb.common.screen.text.GuiTextElectricProgress;
import com.maciej916.indreb.common.screen.widgets.GuiText;
import com.maciej916.indreb.common.tier.ChargePadTier;
import com.maciej916.indreb.common.util.TextComponentUtil;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.network.chat.TranslatableComponent;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Inventory;

public class ScreenChargePad extends BetterScreen<ContainerChargePad> {
   public ScreenChargePad(ContainerChargePad container, Inventory inv, Component name) {
      super(container, inv, name);
   }

   public void m_7856_() {
      super.m_7856_();
      BasicEnergyStorage energyStorage = this.getBlockEntity().getEnergyStorage();
      BlockChargePad block = (BlockChargePad)this.getBlockEntity().getBlock();
      ChargePadTier chargePadTier = block.getChargePadTier();
      this.addRenderableOnlyComponent(new GuiTextElectricProgress(this, 50, 10, 90, 24, energyStorage));
      this.addRenderableOnlyComponent(
         new GuiText(
            this,
            50,
            10,
            90,
            58,
            TextComponentUtil.build(
               new MutableComponent[]{
                  new TranslatableComponent(EnumLang.TRANSFER.getTranslationKey()),
                  new TranslatableComponent(
                     EnumLang.POWER_TICK.getTranslationKey(),
                     new Object[]{TextComponentUtil.getFormattedEnergyUnit((float)chargePadTier.getEnergyTier().getBasicTransfer())}
                  )
               }
            )
         )
      );
      this.drawComponents(true);
   }

   public ResourceLocation getGuiLocation() {
      return new ResourceLocation("indreb", "textures/gui/container/charge_pad.png");
   }
}
