package com.maciej916.indreb.common.block.impl.machines.iron_furnace;

import com.maciej916.indreb.common.block.BlockMachine;
import com.maciej916.indreb.common.interfaces.block.IHasContainer;
import com.maciej916.indreb.common.interfaces.block.IStateActive;
import com.maciej916.indreb.common.interfaces.block.IStateFacing;
import com.maciej916.indreb.common.util.BlockStateHelper;
import java.util.Random;
import javax.annotation.Nullable;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.Direction.Axis;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

public class BlockIronFurnace extends BlockMachine implements IStateFacing, IHasContainer, IStateActive {
   public BlockIronFurnace() {
      super(12, 0);
   }

   @Nullable
   public BlockEntity m_142194_(BlockPos pos, BlockState state) {
      return new BlockEntityIronFurnace(pos, state);
   }

   public ContainerIronFurnace getContainer(int windowId, Level level, BlockPos pos, Inventory playerInventory, Player playerEntity) {
      return new ContainerIronFurnace(windowId, level, pos, playerInventory, playerEntity);
   }

   @OnlyIn(Dist.CLIENT)
   public void m_7100_(BlockState stateIn, Level pLevel, BlockPos pos, Random rand) {
      if ((Boolean)stateIn.m_61143_(BlockStateHelper.activeProperty)) {
         double d0 = (double)pos.m_123341_() + 0.5;
         double d1 = (double)pos.m_123342_();
         double d2 = (double)pos.m_123343_() + 0.5;
         if (rand.nextDouble() < 0.1) {
            pLevel.m_7785_(d0, d1, d2, SoundEvents.f_11907_, SoundSource.BLOCKS, 1.0F, 1.0F, false);
         }

         Direction direction = this.getDirection(stateIn);
         Axis direction$axis = direction.m_122434_();
         double d3 = 0.52;
         double d4 = rand.nextDouble() * 0.6 - 0.3;
         double d5 = direction$axis == Axis.X ? (double)direction.m_122429_() * d3 : d4;
         double d6 = rand.nextDouble() * 6.0 / 16.0;
         double d7 = direction$axis == Axis.Z ? (double)direction.m_122431_() * d3 : d4;
         pLevel.m_7106_(ParticleTypes.f_123762_, d0 + d5, d1 + d6, d2 + d7, 0.0, 0.0, 0.0);
         pLevel.m_7106_(ParticleTypes.f_123744_, d0 + d5, d1 + d6, d2 + d7, 0.0, 0.0, 0.0);
      }
   }
}
