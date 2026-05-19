package com.maciej916.indreb.common.block.impl.luminator;

import com.maciej916.indreb.common.energy.interfaces.IEnergyBlock;
import com.maciej916.indreb.common.entity.block.IndRebBlockEntity;
import com.maciej916.indreb.common.enums.EnergyTier;
import com.maciej916.indreb.common.enums.EnergyType;
import com.maciej916.indreb.common.registries.ModBlockEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.level.block.state.BlockState;

public class BlockEntityLuminator extends IndRebBlockEntity implements IEnergyBlock {
   private boolean active = false;

   public BlockEntityLuminator(BlockPos pWorldPosition, BlockState pBlockState) {
      super(ModBlockEntities.LUMINATOR, pWorldPosition, pBlockState);
      this.createEnergyStorage(0, 1, EnergyType.RECEIVE, EnergyTier.ULTRA);
   }

   @Override
   public void tickOperate(BlockState state) {
      this.active = false;
      this.getEnergyStorage().updateConsumed(0);
      if (this.getEnergyStorage().energyStored() == 1) {
         this.active = true;
         this.getEnergyStorage().consumeEnergy(1, false);
         this.getEnergyStorage().updateConsumed(1);
      }

      this.setActive(this.active);
   }

   @Override
   public boolean canReceiveEnergyDir(Direction side) {
      return true;
   }

   @Override
   public void m_142466_(CompoundTag tag) {
      super.m_142466_(tag);
      this.active = tag.m_128471_("active");
   }

   @Override
   public CompoundTag save(CompoundTag tag) {
      tag.m_128379_("active", this.active);
      return super.save(tag);
   }
}
