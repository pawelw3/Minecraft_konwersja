package com.maciej916.indreb.common.block.impl.cable;

import com.maciej916.indreb.common.energy.interfaces.IEnergyCore;
import com.maciej916.indreb.common.energy.interfaces.IEnergyTransmitter;
import com.maciej916.indreb.common.energy.provider.EnergyNetwork;
import com.maciej916.indreb.common.registries.ModBlockEntities;
import com.maciej916.indreb.common.registries.ModCapabilities;
import com.maciej916.indreb.common.util.CapabilityUtil;
import com.maciej916.indreb.common.util.LazyOptionalHelper;
import javax.annotation.Nonnull;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.common.capabilities.Capability;
import net.minecraftforge.common.util.LazyOptional;

public class BlockEntityCable extends BlockEntity implements IEnergyTransmitter {
   private final LazyOptional<IEnergyTransmitter> energyTransmitter = LazyOptional.of(() -> this);

   public BlockEntityCable(BlockPos pWorldPosition, BlockState pBlockState) {
      super(ModBlockEntities.CABLE, pWorldPosition, pBlockState);
   }

   @Nonnull
   public <T> LazyOptional<T> getCapability(@Nonnull Capability<T> cap) {
      return cap == ModCapabilities.ENERGY_TRANSMITTER ? this.energyTransmitter.cast() : super.getCapability(cap);
   }

   public EnergyNetwork getNetwork() {
      LazyOptionalHelper<IEnergyCore> cap = CapabilityUtil.getCapabilityHelper(this.m_58904_(), ModCapabilities.ENERGY_CORE, null);
      return (EnergyNetwork)cap.getIfPresentElse(e -> e.getNetworks().getNetwork(this.m_58899_()), null);
   }
}
