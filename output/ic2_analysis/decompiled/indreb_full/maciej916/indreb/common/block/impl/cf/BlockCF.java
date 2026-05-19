package com.maciej916.indreb.common.block.impl.cf;

import com.maciej916.indreb.common.registries.ModBlocks;
import java.util.Random;
import java.util.concurrent.ThreadLocalRandom;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.AbstractGlassBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.BlockBehaviour.Properties;
import net.minecraft.world.level.material.Material;
import net.minecraft.world.level.material.MaterialColor;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

public class BlockCF extends AbstractGlassBlock {
   protected static final VoxelShape SHAPE = Block.m_49796_(4.0, 0.0, 4.0, 12.0, 12.0, 12.0);

   public BlockCF() {
      super(Properties.m_60944_(Material.f_76320_, MaterialColor.f_76401_).m_60913_(0.5F, 3.0F).m_60918_(SoundType.f_56745_).m_60977_().m_60955_());
   }

   public VoxelShape m_5939_(BlockState p_54015_, BlockGetter p_54016_, BlockPos p_54017_, CollisionContext p_54018_) {
      return SHAPE;
   }

   public void m_7458_(BlockState pState, ServerLevel pLevel, BlockPos pPos, Random pRandom) {
      int count = ThreadLocalRandom.current().nextInt(0, 3);
      if (count == 0) {
         pLevel.m_7731_(pPos, ModBlocks.CONSTRUCTION_FOAM_WALL_LIGHT_GRAY.m_40614_().m_49966_(), 2);
      }

      super.m_7458_(pState, pLevel, pPos, pRandom);
   }
}
