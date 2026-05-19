package com.maciej916.indreb.common.block.impl.battery_box;

import com.maciej916.indreb.common.energy.impl.BasicEnergyStorage;
import com.maciej916.indreb.common.enums.EnumLang;
import com.maciej916.indreb.common.screen.BetterScreen;
import com.maciej916.indreb.common.screen.text.GuiTextElectricProgress;
import com.maciej916.indreb.common.screen.widgets.GuiText;
import com.maciej916.indreb.common.tier.BatteryBoxTier;
import com.maciej916.indreb.common.util.TextComponentUtil;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.network.chat.TranslatableComponent;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Inventory;

public class ScreenBatteryBox extends BetterScreen<ContainerBatteryBox> {
   public ScreenBatteryBox(ContainerBatteryBox container, Inventory inv, Component name) {
      super(container, inv, name);
      this.f_97727_ = 266;
      this.f_97731_ = 104;
   }

   public void m_7856_() {
      super.m_7856_();
      BasicEnergyStorage energyStorage = this.getBlockEntity().getEnergyStorage();
      BlockBatteryBox block = (BlockBatteryBox)this.getBlockEntity().getBlock();
      BatteryBoxTier batteryBoxTier = block.getBatteryBoxTier();
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
                     new Object[]{TextComponentUtil.getFormattedEnergyUnit((float)batteryBoxTier.getEnergyTier().getBasicTransfer())}
                  )
               }
            )
         )
      );
      this.drawComponents(true);
   }

   protected void m_7027_(PoseStack poseStack, int mouseX, int mouseY) {
      super.m_7027_(poseStack, mouseX, mouseY);
      this.f_96547_.m_92889_(poseStack, EnumLang.ARMOUR.getTranslationComponent(), 8.0F, 72.0F, 4210752);
   }

   public ResourceLocation getGuiLocation() {
      return new ResourceLocation("indreb", "textures/gui/container/battery_box.png");
   }
}
