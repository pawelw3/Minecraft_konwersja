package com.maciej916.indreb.common.block.impl.generators.solar_panels;

import com.maciej916.indreb.common.energy.interfaces.IEnergyBlock;
import com.maciej916.indreb.common.entity.block.IndRebBlockEntity;
import com.maciej916.indreb.common.enums.EnergyTier;
import com.maciej916.indreb.common.enums.EnergyType;
import com.maciej916.indreb.common.interfaces.entity.ITileSound;
import com.maciej916.indreb.common.registries.ModBlockEntities;
import com.maciej916.indreb.common.registries.ModSounds;
import com.maciej916.indreb.common.tier.SolarGeneratorTier;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.level.block.state.BlockState;

public class BlockEntitySolarGenerator extends IndRebBlockEntity implements IEnergyBlock, ITileSound {
   private final SolarGeneratorTier tier;
   private boolean active = false;
   private int lastAmount = 0;
   public int amount = 0;

   public BlockEntitySolarGenerator(BlockPos pWorldPosition, BlockState pBlockState) {
      super(ModBlockEntities.SOLAR_GENERATOR, pWorldPosition, pBlockState);
      BlockSolarGenerator block = (BlockSolarGenerator)this.getBlock();
      this.tier = block.getSolarGeneratorTier();
      EnergyTier energyTier = this.tier.getEnergyTier();
      this.createEnergyStorage(0, this.tier.getEnergyCapacity(), EnergyType.EXTRACT, energyTier);
   }

   @Override
   public boolean getActive() {
      return super.getActive();
   }

   @Override
   public void tickOperate(BlockState state) {
      this.active = false;
      this.amount = 0;
      this.getEnergyStorage().updateGenerated(0);
      if (this.f_58857_ != null && this.f_58857_.m_45527_(this.m_58899_())) {
         if (this.f_58857_.m_46461_() && !this.f_58857_.m_46470_()) {
            this.amount = this.tier.getDayGenerate();
         }

         if (!this.f_58857_.m_46461_() || this.f_58857_.m_46470_() || this.f_58857_.m_46471_()) {
            this.amount = this.tier.getNightGenerate();
         }
      }

      if (this.amount > 0) {
         this.active = true;
         if (this.getEnergyStorage().generateEnergy(this.amount, true) == this.amount) {
            this.getEnergyStorage().generateEnergy(this.amount, false);
            this.getEnergyStorage().updateGenerated(this.amount);
         }
      }

      if (this.amount != this.lastAmount) {
         this.lastAmount = this.amount;
         super.updateBlockState();
      }

      if (this.setActive(this.active)) {
         super.updateBlockState();
      }
   }

   @Override
   public void m_142466_(CompoundTag tag) {
      super.m_142466_(tag);
      this.active = tag.m_128471_("active");
      this.amount = tag.m_128451_("amount");
      this.lastAmount = tag.m_128451_("lastAmount");
   }

   @Override
   public CompoundTag save(CompoundTag tag) {
      tag.m_128379_("active", this.active);
      tag.m_128405_("amount", this.amount);
      tag.m_128405_("lastAmount", this.lastAmount);
      return super.save(tag);
   }

   public SoundEvent getSoundEvent() {
      return ModSounds.SOLAR_GENERATOR;
   }

   @Override
   public boolean canExtractEnergyDir(Direction side) {
      return side == Direction.DOWN ? true : super.canExtractEnergyDir(side);
   }

   public boolean showInGui() {
      return false;
   }
}
