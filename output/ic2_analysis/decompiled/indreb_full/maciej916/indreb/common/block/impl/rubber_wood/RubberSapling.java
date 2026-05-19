package com.maciej916.indreb.common.block.impl.rubber_wood;

import net.minecraft.world.level.block.SaplingBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.grower.AbstractTreeGrower;
import net.minecraft.world.level.block.state.BlockBehaviour.Properties;
import net.minecraft.world.level.material.Material;

public class RubberSapling extends SaplingBlock {
   public RubberSapling(AbstractTreeGrower tree) {
      super(tree, Properties.m_60939_(Material.f_76300_).m_60910_().m_60977_().m_60978_(0.0F).m_60966_().m_60918_(SoundType.f_56740_));
   }
}
