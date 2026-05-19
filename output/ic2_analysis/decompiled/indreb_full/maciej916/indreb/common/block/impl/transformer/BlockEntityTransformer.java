package com.maciej916.indreb.common.block.impl.transformer;

import com.maciej916.indreb.common.energy.interfaces.IEnergyBlock;
import com.maciej916.indreb.common.entity.block.IndRebBlockEntity;
import com.maciej916.indreb.common.enums.EnergyTier;
import com.maciej916.indreb.common.enums.EnergyType;
import com.maciej916.indreb.common.enums.TransformerMode;
import com.maciej916.indreb.common.interfaces.block.IStateFacing;
import com.maciej916.indreb.common.network.ModNetworking;
import com.maciej916.indreb.common.network.packet.PacketTransformerMode;
import com.maciej916.indreb.common.registries.ModBlockEntities;
import com.maciej916.indreb.common.tier.TransformerTier;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.level.block.state.BlockState;

public class BlockEntityTransformer extends IndRebBlockEntity implements IEnergyBlock {
   private final TransformerTier tier;
   private boolean init = false;
   private TransformerMode transformerMode;
   private EnergyTier minTier;
   private EnergyTier maxTier;

   public BlockEntityTransformer(BlockPos pWorldPosition, BlockState pBlockState) {
      super(ModBlockEntities.TRANSFORMER, pWorldPosition, pBlockState);
      BlockTransformer block = (BlockTransformer)this.getBlock();
      this.tier = block.getTransformerTier();
      this.createEnergyStorage(0, this.tier.getMaxTier().getBasicTransfer(), EnergyType.TRANSFORMER, this.tier.getMaxTier());
      this.transformerMode = TransformerMode.STEP_UP;
      this.initMode();
   }

   public TransformerTier getTransformerTier() {
      return this.tier;
   }

   public TransformerMode getTransformerMode() {
      return this.transformerMode;
   }

   public boolean showInGui() {
      return false;
   }

   @Override
   public boolean canExtractEnergyDir(Direction side) {
      if (side == null) {
         return true;
      } else {
         IStateFacing blockFacing = (IStateFacing)this.getBlock();
         Direction facingDirection = blockFacing.getDirection(this.m_58900_());
         return this.transformerMode == TransformerMode.STEP_UP == (facingDirection == side);
      }
   }

   @Override
   public boolean canReceiveEnergyDir(Direction side) {
      if (side == null) {
         return true;
      } else {
         IStateFacing blockFacing = (IStateFacing)this.getBlock();
         Direction facingDirection = blockFacing.getDirection(this.m_58900_());
         return this.transformerMode == TransformerMode.STEP_UP == (facingDirection != side);
      }
   }

   public boolean showVertical() {
      return false;
   }

   @Override
   public int customEnergyExtractTick() {
      return this.energyExtractTier().getBasicTransfer();
   }

   @Override
   public int customEnergyReceiveTick() {
      return this.energyReceiveTier().getBasicTransfer();
   }

   public EnergyTier energyExtractTier() {
      return this.maxTier;
   }

   public EnergyTier energyReceiveTier() {
      return this.minTier;
   }

   private void initMode() {
      if (this.transformerMode == TransformerMode.STEP_UP) {
         this.minTier = this.tier.getMinTier();
         this.maxTier = this.tier.getMaxTier();
      } else {
         this.minTier = this.tier.getMaxTier();
         this.maxTier = this.tier.getMinTier();
      }

      this.init = true;
   }

   public void updateMode() {
      if (this.transformerMode == TransformerMode.STEP_UP) {
         this.minTier = this.tier.getMaxTier();
         this.maxTier = this.tier.getMinTier();
         this.transformerMode = TransformerMode.STEP_DOWN;
      } else {
         this.minTier = this.tier.getMinTier();
         this.maxTier = this.tier.getMaxTier();
         this.transformerMode = TransformerMode.STEP_UP;
      }

      this.updateBlockState();
   }

   public Runnable changeMode() {
      return () -> ModNetworking.INSTANCE.sendToServer(new PacketTransformerMode(this.m_58899_()));
   }

   @Override
   public void m_142466_(CompoundTag tag) {
      super.m_142466_(tag);
      this.transformerMode = TransformerMode.getMode(tag.m_128451_("transformerMode"));
      if (!this.init) {
         this.initMode();
      }
   }

   @Override
   public CompoundTag save(CompoundTag tag) {
      tag.m_128405_("transformerMode", this.transformerMode.getMode());
      return super.save(tag);
   }
}
