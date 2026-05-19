package com.maciej916.indreb.common.block.impl.cf;

import net.minecraft.world.level.block.AbstractGlassBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour.Properties;
import net.minecraft.world.level.material.Material;
import net.minecraft.world.level.material.MaterialColor;

public class BlockReinforcedGlass extends AbstractGlassBlock {
   public BlockReinforcedGlass() {
      super(Properties.m_60944_(Material.f_76275_, MaterialColor.f_76362_).m_60913_(10.0F, 1.0E10F).m_60918_(SoundType.f_56744_).m_60955_());
   }
}
