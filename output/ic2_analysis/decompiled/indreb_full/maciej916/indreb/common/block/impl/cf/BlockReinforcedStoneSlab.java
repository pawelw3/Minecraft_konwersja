package com.maciej916.indreb.common.block.impl.cf;

import net.minecraft.world.level.block.SlabBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour.Properties;
import net.minecraft.world.level.material.Material;
import net.minecraft.world.level.material.MaterialColor;

public class BlockReinforcedStoneSlab extends SlabBlock {
   public BlockReinforcedStoneSlab() {
      super(Properties.m_60944_(Material.f_76278_, MaterialColor.f_76409_).m_60913_(10.0F, 1.0E10F).m_60918_(SoundType.f_56742_));
   }
}
