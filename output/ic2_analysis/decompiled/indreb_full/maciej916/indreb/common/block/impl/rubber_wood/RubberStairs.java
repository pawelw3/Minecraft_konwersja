package com.maciej916.indreb.common.block.impl.rubber_wood;

import com.maciej916.indreb.common.registries.ModBlocks;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.StairBlock;
import net.minecraft.world.level.block.state.BlockBehaviour.Properties;
import net.minecraft.world.level.material.Material;
import net.minecraft.world.level.material.MaterialColor;

public class RubberStairs extends StairBlock {
   public RubberStairs() {
      super(
         () -> ModBlocks.RUBBER_PLANKS.m_40614_().m_49966_(),
         Properties.m_60944_(Material.f_76320_, MaterialColor.f_76362_).m_60913_(2.0F, 3.0F).m_60918_(SoundType.f_56736_)
      );
   }
}
