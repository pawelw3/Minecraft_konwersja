package com.maciej916.indreb.common.block.impl.generators.solar_panels;

import com.maciej916.indreb.common.screen.BetterScreen;
import com.maciej916.indreb.common.screen.active.GuiSolarActive;
import com.maciej916.indreb.common.screen.text.GuiTextSolar;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Inventory;

public class ScreenSolarGenerator extends BetterScreen<ContainerSolarGenerator> {
   public ScreenSolarGenerator(ContainerSolarGenerator container, Inventory inv, Component name) {
      super(container, inv, name);
   }

   public void m_7856_() {
      super.m_7856_();
      this.addRenderableOnlyComponent(new GuiSolarActive(this, 80, 25, ((BlockEntitySolarGenerator)this.getBlockEntity()).getActive()));
      this.addRenderableOnlyComponent(new GuiTextSolar(this, 60, 18, 88, 47, (BlockEntitySolarGenerator)this.getBlockEntity()));
      this.drawComponents(true);
   }

   public ResourceLocation getGuiLocation() {
      return new ResourceLocation("indreb", "textures/gui/container/solar_generator.png");
   }
}
