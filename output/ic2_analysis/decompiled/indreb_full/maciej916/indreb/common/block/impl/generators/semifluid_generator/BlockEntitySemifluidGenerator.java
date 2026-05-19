package com.maciej916.indreb.common.block.impl.generators.semifluid_generator;

import com.maciej916.indreb.common.config.ServerConfig;
import com.maciej916.indreb.common.energy.interfaces.IEnergyBlock;
import com.maciej916.indreb.common.entity.block.BlockEntityProgress;
import com.maciej916.indreb.common.entity.block.FluidStorage;
import com.maciej916.indreb.common.entity.block.IndRebBlockEntity;
import com.maciej916.indreb.common.entity.slot.IndRebSlot;
import com.maciej916.indreb.common.entity.slot.SlotBattery;
import com.maciej916.indreb.common.enums.EnergyTier;
import com.maciej916.indreb.common.enums.EnergyType;
import com.maciej916.indreb.common.enums.GuiSlotType;
import com.maciej916.indreb.common.enums.InventorySlotType;
import com.maciej916.indreb.common.fluids.Biogas;
import com.maciej916.indreb.common.interfaces.entity.ICooldown;
import com.maciej916.indreb.common.interfaces.entity.IElectricSlot;
import com.maciej916.indreb.common.interfaces.entity.ITileSound;
import com.maciej916.indreb.common.registries.ModBlockEntities;
import com.maciej916.indreb.common.registries.ModSounds;
import com.maciej916.indreb.common.util.BlockEntityUtil;
import com.maciej916.indreb.common.util.CapabilityUtil;
import com.maciej916.indreb.common.util.LazyOptionalHelper;
import java.util.ArrayList;
import java.util.Arrays;
import javax.annotation.Nonnull;
import javax.annotation.Nullable;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.common.capabilities.Capability;
import net.minecraftforge.common.util.LazyOptional;
import net.minecraftforge.fluids.capability.CapabilityFluidHandler;
import net.minecraftforge.fluids.capability.IFluidHandlerItem;
import net.minecraftforge.items.CapabilityItemHandler;
import net.minecraftforge.items.wrapper.RangedWrapper;

public class BlockEntitySemifluidGenerator extends IndRebBlockEntity implements ICooldown, IEnergyBlock, ITileSound {
   public static final int FILL_BUCKET_UP = 0;
   public static final int FILL_BUCKET_DOWN = 1;
   public BlockEntityProgress progressFill = new BlockEntityProgress(0, 1);
   private boolean active = false;
   public FluidStorage fluidStorage = new FluidStorage(
      (Integer)ServerConfig.semifluid_generator_fluid_capacity.get(), fluidStack -> fluidStack.getFluid() == Biogas.STILL_FLUID
   );
   private int cachedFluid = 0;
   private final ArrayList<LazyOptional<?>> capabilities = new ArrayList<>(
      Arrays.asList(
         LazyOptional.of(this::getStackHandler),
         LazyOptional.of(() -> new RangedWrapper(this.getStackHandler(), 0, 1)),
         LazyOptional.of(() -> new RangedWrapper(this.getStackHandler(), 1, 2)),
         LazyOptional.of(() -> this.fluidStorage)
      )
   );

   public BlockEntitySemifluidGenerator(BlockPos pWorldPosition, BlockState pBlockState) {
      super(ModBlockEntities.SEMIFLUID_GENERATOR, pWorldPosition, pBlockState);
      this.createEnergyStorage(0, (Integer)ServerConfig.semifluid_generator_energy_capacity.get(), EnergyType.EXTRACT, EnergyTier.BASIC);
   }

   @Override
   public ArrayList<IndRebSlot> addInventorySlot(ArrayList<IndRebSlot> slots) {
      slots.add(new IndRebSlot(0, 61, 20, InventorySlotType.INPUT, GuiSlotType.NORMAL, 60, 19));
      slots.add(new IndRebSlot(1, 61, 51, InventorySlotType.OUTPUT, GuiSlotType.NORMAL, 60, 50));
      return super.addInventorySlot(slots);
   }

   @Override
   public void tickOperate(BlockState state) {
      this.active = false;
      boolean updateState = false;
      this.getEnergyStorage().updateGenerated(0);
      ItemStack fillBucketUp = this.getStackHandler().getStackInSlot(0);
      ItemStack fillBucketDown = this.getStackHandler().getStackInSlot(1);
      if (this.progressFill.getProgress() == 0.0F) {
         boolean filled = BlockEntityUtil.fillTank(fillBucketUp, fillBucketDown, this.fluidStorage, this.getStackHandler(), 1);
         if (filled) {
            this.progressFill.setProgress(1.0F);
         }
      } else {
         this.progressFill.setProgress(0.0F);
      }

      if (this.progressFill.changed()) {
         updateState = true;
      }

      if (this.cachedFluid != this.fluidStorage.getFluidAmount()) {
         this.cachedFluid = this.fluidStorage.getFluidAmount();
         updateState = true;
      }

      if (this.getCooldown() == 0) {
         if (this.getEnergyStorage().generateEnergy((Integer)ServerConfig.semifluid_generator_tick_generate.get(), true)
               == (Integer)ServerConfig.semifluid_generator_tick_generate.get()
            && this.fluidStorage.takeFluid(1, true) == 1) {
            this.fluidStorage.takeFluid(1, false);
            this.getEnergyStorage().generateEnergy((Integer)ServerConfig.semifluid_generator_tick_generate.get(), false);
            this.getEnergyStorage().updateGenerated((Integer)ServerConfig.semifluid_generator_tick_generate.get());
            this.active = true;
            updateState = true;
         }

         if (this.active
            && this.getEnergyStorage().generateEnergy((Integer)ServerConfig.semifluid_generator_tick_generate.get(), true)
               < (Integer)ServerConfig.semifluid_generator_tick_generate.get()
            && this.fluidStorage.takeFluid(1, true) == 1) {
            this.setCooldown(10);
         }
      }

      if (this.getActive() != this.active) {
         this.setActive(this.active);
         updateState = true;
      }

      if (updateState) {
         this.updateBlockState();
      }
   }

   @Override
   public boolean isItemValidForSlot(int slot, @Nonnull ItemStack stack) {
      if (slot == 0) {
         LazyOptionalHelper<IFluidHandlerItem> cap = CapabilityUtil.getCapabilityHelper(stack, CapabilityFluidHandler.FLUID_HANDLER_ITEM_CAPABILITY);
         return !cap.isPresent()
            ? false
            : ((IFluidHandlerItem)cap.getValue()).getTanks() > 0 && ((IFluidHandlerItem)cap.getValue()).getFluidInTank(1).getFluid() == Biogas.STILL_FLUID;
      } else {
         return slot == 1 ? false : super.isItemValidForSlot(slot, stack);
      }
   }

   @Override
   public ItemStack insertItemForSlot(int slot, @Nonnull ItemStack stack, boolean simulate) {
      if (slot == 0) {
         LazyOptionalHelper<IFluidHandlerItem> cap = CapabilityUtil.getCapabilityHelper(stack, CapabilityFluidHandler.FLUID_HANDLER_ITEM_CAPABILITY);
         return cap.isPresent()
               && ((IFluidHandlerItem)cap.getValue()).getTanks() > 0
               && ((IFluidHandlerItem)cap.getValue()).getFluidInTank(1).getFluid() == Biogas.STILL_FLUID
            ? null
            : stack;
      } else {
         return slot == 1 ? stack : super.insertItemForSlot(slot, stack, simulate);
      }
   }

   @Override
   public void m_142466_(CompoundTag tag) {
      super.m_142466_(tag);
      this.fluidStorage.readFromNBT(tag.m_128469_("fluidStorage"));
      this.active = tag.m_128471_("active");
      this.progressFill.deserializeNBT(tag.m_128469_("fill"));
   }

   @Override
   public CompoundTag save(CompoundTag tag) {
      tag.m_128365_("fluidStorage", this.fluidStorage.writeToNBT(tag.m_128469_("fluidStorage")));
      tag.m_128379_("active", this.active);
      tag.m_128365_("fill", this.progressFill.serializeNBT());
      return super.save(tag);
   }

   @Override
   public ArrayList<IElectricSlot> addBatterySlot(ArrayList<IElectricSlot> slots) {
      slots.add(new SlotBattery(0, 152, 62, true));
      return super.addBatterySlot(slots);
   }

   public SoundEvent getSoundEvent() {
      return ModSounds.SEMIFLUID_GENERATOR;
   }

   @Override
   public boolean canExtractEnergyDir(Direction side) {
      return true;
   }

   @Nonnull
   @Override
   public <T> LazyOptional<T> getCapability(@Nonnull Capability<T> cap, @Nullable Direction side) {
      if (cap == CapabilityFluidHandler.FLUID_HANDLER_CAPABILITY) {
         return this.capabilities.get(3).cast();
      } else if (cap == CapabilityItemHandler.ITEM_HANDLER_CAPABILITY) {
         if (side == null) {
            return this.capabilities.get(0).cast();
         } else {
            return switch (side) {
               case DOWN -> this.capabilities.get(2).cast();
               case UP, NORTH, SOUTH, WEST, EAST -> this.capabilities.get(1).cast();
               default -> throw new IncompatibleClassChangeError();
            };
         }
      } else {
         return super.getCapability(cap, side);
      }
   }

   @Override
   public void onBreak() {
      for (LazyOptional<?> capability : this.capabilities) {
         capability.invalidate();
      }

      super.onBreak();
   }
}
