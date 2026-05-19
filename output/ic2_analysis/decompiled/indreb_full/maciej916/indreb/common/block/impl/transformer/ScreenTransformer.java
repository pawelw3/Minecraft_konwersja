package com.maciej916.indreb.common.block.impl.transformer;

import com.maciej916.indreb.common.screen.BetterScreen;
import com.maciej916.indreb.common.screen.button.GuiTransformerButton;
import com.maciej916.indreb.common.screen.widgets.GuiText;
import com.maciej916.indreb.common.screen.widgets.GuiTransformerInfo;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.TranslatableComponent;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Inventory;

public class ScreenTransformer extends BetterScreen<ContainerTransformer> {
   public ScreenTransformer(ContainerTransformer container, Inventory inv, Component name) {
      super(container, inv, name);
   }

   public void m_7856_() {
      super.m_7856_();
      BlockEntityTransformer be = (BlockEntityTransformer)this.getBlockEntity();
      this.addRenderableOnlyComponent(new GuiText(this, 88, 5, 8, 30, new TranslatableComponent("gui.indreb.input")));
      this.addRenderableOnlyComponent(new GuiText(this, 88, 5, 8, 46, new TranslatableComponent("gui.indreb.output")));
      this.addRenderableOnlyComponent(new GuiTransformerInfo(this, be));
      this.addRenderableComponent(new GuiTransformerButton(this, 140, 32, be.changeMode()));
      this.drawComponents(true);
   }

   public ResourceLocation getGuiLocation() {
      return new ResourceLocation("indreb", "textures/gui/container/transformer.png");
   }
}
