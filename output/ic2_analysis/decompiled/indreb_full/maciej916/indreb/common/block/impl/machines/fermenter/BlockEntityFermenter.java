package com.maciej916.indreb.common.block.impl.machines.fermenter;

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
import com.maciej916.indreb.common.enums.UpgradeType;
import com.maciej916.indreb.common.fluids.Biogas;
import com.maciej916.indreb.common.fluids.Biomass;
import com.maciej916.indreb.common.interfaces.block.IStateFacing;
import com.maciej916.indreb.common.interfaces.entity.IElectricSlot;
import com.maciej916.indreb.common.interfaces.entity.ISupportUpgrades;
import com.maciej916.indreb.common.registries.ModBlockEntities;
import com.maciej916.indreb.common.registries.ModItems;
import com.maciej916.indreb.common.util.BlockEntityUtil;
import com.maciej916.indreb.common.util.CapabilityUtil;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import javax.annotation.Nonnull;
import javax.annotation.Nullable;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.material.Fluids;
import net.minecraftforge.common.capabilities.Capability;
import net.minecraftforge.common.util.LazyOptional;
import net.minecraftforge.fluids.FluidStack;
import net.minecraftforge.fluids.capability.CapabilityFluidHandler;
import net.minecraftforge.fluids.capability.IFluidHandlerItem;
import net.minecraftforge.fluids.capability.IFluidHandler.FluidAction;
import net.minecraftforge.items.CapabilityItemHandler;
import net.minecraftforge.items.wrapper.RangedWrapper;

public class BlockEntityFermenter extends IndRebBlockEntity implements IEnergyBlock, ISupportUpgrades {
   public static final int FILL_BUCKET_UP = 0;
   public static final int FILL_BUCKET_DOWN = 2;
   public static final int WASTE_SLOT = 3;
   public static final int DRAIN_BUCKET_UP = 1;
   public static final int DRAIN_BUCKET_DOWN = 4;
   private boolean active = false;
   public FluidStorage fluidInputStorage = new FluidStorage(
      (Integer)ServerConfig.fermenter_biomass_capacity.get(), fluidStack -> fluidStack.getFluid() == Biomass.STILL_FLUID
   );
   public FluidStorage fluidOutputStorage = new FluidStorage((Integer)ServerConfig.fermenter_biogas_capacity.get());
   private int cachedInput = 0;
   private int cachedOutput = 0;
   public BlockEntityProgress progress = new BlockEntityProgress();
   public BlockEntityProgress progressWaste = new BlockEntityProgress();
   public BlockEntityProgress heatLevel = new BlockEntityProgress(0, 100);
   public BlockEntityProgress progressFill = new BlockEntityProgress(0, 1);
   public BlockEntityProgress progressDrain = new BlockEntityProgress(0, 1);
   private final ArrayList<LazyOptional<?>> capabilities = new ArrayList<>(
      Arrays.asList(
         LazyOptional.of(this::getStackHandler),
         LazyOptional.of(() -> new RangedWrapper(this.getStackHandler(), 0, 2)),
         LazyOptional.of(() -> new RangedWrapper(this.getStackHandler(), 2, 5)),
         LazyOptional.of(() -> this.fluidInputStorage),
         LazyOptional.of(() -> this.fluidOutputStorage)
      )
   );

   public BlockEntityFermenter(BlockPos pWorldPosition, BlockState pBlockState) {
      super(ModBlockEntities.FERMENTER, pWorldPosition, pBlockState);
      this.createEnergyStorage(0, (Integer)ServerConfig.fermenter_energy_capacity.get(), EnergyType.RECEIVE, EnergyTier.STANDARD);
   }

   @Override
   public ArrayList<IndRebSlot> addInventorySlot(ArrayList<IndRebSlot> slots) {
      slots.add(new IndRebSlot(0, 13, 19, InventorySlotType.INPUT, GuiSlotType.NORMAL, 12, 18));
      slots.add(new IndRebSlot(2, 13, 50, InventorySlotType.OUTPUT, GuiSlotType.NORMAL, 12, 49));
      slots.add(new IndRebSlot(3, 51, 73, InventorySlotType.OUTPUT, GuiSlotType.NORMAL, 50, 72));
      slots.add(new IndRebSlot(1, 127, 19, InventorySlotType.INPUT, GuiSlotType.NORMAL, 126, 18));
      slots.add(new IndRebSlot(4, 127, 50, InventorySlotType.OUTPUT, GuiSlotType.NORMAL, 126, 49));
      return super.addInventorySlot(slots);
   }

   @Override
   public ArrayList<IElectricSlot> addBatterySlot(ArrayList<IElectricSlot> slots) {
      slots.add(new SlotBattery(0, 152, 62, false));
      return super.addBatterySlot(slots);
   }

   @Override
   public void tickOperate(BlockState state) {
      this.active = false;
      boolean updateState = false;
      this.getEnergyStorage().updateConsumed(0);
      ItemStack fillBucketUp = this.getStackHandler().getStackInSlot(0);
      ItemStack fillBucketDown = this.getStackHandler().getStackInSlot(2);
      ItemStack drainBucketUp = this.getStackHandler().getStackInSlot(1);
      ItemStack drainBucketDown = this.getStackHandler().getStackInSlot(4);
      ItemStack wasteStack = this.getStackHandler().getStackInSlot(3);
      if (this.progressFill.getProgress() == 0.0F) {
         boolean filled = BlockEntityUtil.fillTank(fillBucketUp, fillBucketDown, this.fluidInputStorage, this.getStackHandler(), 2);
         if (filled) {
            this.progressFill.setProgress(1.0F);
         }
      } else {
         this.progressFill.setProgress(0.0F);
      }

      if (this.progressFill.changed()) {
         updateState = true;
      }

      if (this.cachedInput != this.fluidInputStorage.getFluidAmount()) {
         this.cachedInput = this.fluidInputStorage.getFluidAmount();
         updateState = true;
      }

      if (this.progressDrain.getProgress() == 0.0F) {
         boolean drained = BlockEntityUtil.drainTank(drainBucketUp, drainBucketDown, this.fluidOutputStorage, this.getStackHandler(), 1, 4);
         if (drained) {
            this.progressDrain.setProgress(1.0F);
         }
      } else {
         this.progressDrain.setProgress(0.0F);
      }

      if (this.progressDrain.changed()) {
         updateState = true;
      }

      if (this.cachedOutput != this.fluidOutputStorage.getFluidAmount()) {
         this.cachedOutput = this.fluidOutputStorage.getFluidAmount();
         updateState = true;
      }

      this.progress.setProgressMax(this.getSpeedFactor() * 600.0F);
      this.progressWaste.setProgressMax(this.getSpeedFactor() * 1400.0F);
      int energyCost = (int)((float)((Integer)ServerConfig.fermenter_tick_usage.get()).intValue() * this.getEnergyUsageFactor());
      if (this.fluidInputStorage.getFluidAmount() >= 1000
         && this.fluidOutputStorage.getFluidAmount() + 200 <= this.fluidOutputStorage.getCapacity()
         && wasteStack.m_41613_() < wasteStack.m_41741_()) {
         if (this.progress.getProgress() == -1.0F) {
            this.progress.setData(0.0F, 600.0F);
         }

         if (this.progressWaste.getProgress() == -1.0F) {
            this.progressWaste.setData(0.0F, 1400.0F);
         }

         if (this.getEnergyStorage().consumeEnergy(energyCost, true) == energyCost && this.progress.getProgress() <= this.progress.getProgressMax()) {
            this.active = true;
            this.progress.incProgress(1.0F + this.heatLevel.getPercentProgress() / 100.0F);
            this.progressWaste.incProgress(1.0F);
            this.getEnergyStorage().consumeEnergy(energyCost, false);
            this.getEnergyStorage().updateConsumed(energyCost);
         }

         if (this.progress.getProgress() >= this.progress.getProgressMax()) {
            this.fluidInputStorage.drain(1000, FluidAction.EXECUTE);
            this.fluidOutputStorage.fill(new FluidStack(Biogas.STILL_FLUID, 200), FluidAction.EXECUTE);
            this.progress.setBoth(-1.0F);
         }

         if (this.progressWaste.getProgress() >= this.progressWaste.getProgressMax()) {
            if (wasteStack.m_41619_()) {
               this.getStackHandler().setStackInSlot(3, new ItemStack(ModItems.FERTILIZER));
            } else {
               wasteStack.m_41769_(1);
            }

            this.progressWaste.setBoth(-1.0F);
         }
      }

      if (this.progress.changed()) {
         updateState = true;
      }

      if (this.progressWaste.changed()) {
         updateState = true;
      }

      if ((
            this.getRedstonePower() <= 0
               || this.getEnergyStorage().consumeEnergy((Integer)ServerConfig.fermenter_heat_cost.get(), true)
                  < (Integer)ServerConfig.fermenter_heat_cost.get()
         )
         && !this.active) {
         if (this.heatLevel.getProgress() > 0.0F && this.tickCounter == 20) {
            this.heatLevel.decProgress(Math.min(this.heatLevel.getProgress(), 1.0F));
         }
      } else if (this.heatLevel.getProgress() < 100.0F && this.tickCounter == 20) {
         this.heatLevel.incProgress(0.2F);
         if (!this.active) {
            this.getEnergyStorage().consumeEnergy((Integer)ServerConfig.fermenter_heat_cost.get(), false);
         }
      }

      if (this.heatLevel.changed()) {
         updateState = true;
      }

      this.setActive(this.active);
      if (updateState) {
         this.updateBlockState();
      }
   }

   @Override
   public void m_142466_(CompoundTag tag) {
      super.m_142466_(tag);
      this.fluidInputStorage.readFromNBT(tag.m_128469_("fluidInputStorage"));
      this.fluidOutputStorage.readFromNBT(tag.m_128469_("fluidOutputStorage"));
      this.progressFill.deserializeNBT(tag.m_128469_("progressFill"));
      this.progressDrain.deserializeNBT(tag.m_128469_("progressDrain"));
      this.progress.deserializeNBT(tag.m_128469_("progress"));
      this.active = tag.m_128471_("active");
      this.heatLevel.deserializeNBT(tag.m_128469_("heatLevel"));
      this.progressWaste.deserializeNBT(tag.m_128469_("progressWaste"));
   }

   @Override
   public CompoundTag save(CompoundTag tag) {
      tag.m_128365_("fluidInputStorage", this.fluidInputStorage.writeToNBT(tag.m_128469_("fluidInputStorage")));
      tag.m_128365_("fluidOutputStorage", this.fluidOutputStorage.writeToNBT(tag.m_128469_("fluidOutputStorage")));
      tag.m_128365_("progressFill", this.progressFill.serializeNBT());
      tag.m_128365_("progressDrain", this.progressDrain.serializeNBT());
      tag.m_128365_("progress", this.progress.serializeNBT());
      tag.m_128379_("active", this.active);
      tag.m_128365_("heatLevel", this.heatLevel.serializeNBT());
      tag.m_128365_("progressWaste", this.progressWaste.serializeNBT());
      return super.save(tag);
   }

   @Override
   public boolean canReceiveEnergyDir(Direction side) {
      return true;
   }

   @Override
   public boolean isItemValidForSlot(int slot, @Nonnull ItemStack stack) {
      if (slot == 0) {
         IFluidHandlerItem cap = (IFluidHandlerItem)CapabilityUtil.getCapabilityHelper(stack, CapabilityFluidHandler.FLUID_HANDLER_ITEM_CAPABILITY).getValue();
         if (cap != null) {
            return cap.getTanks() > 0 && cap.getFluidInTank(1).getFluid() == Biomass.STILL_FLUID;
         }
      }

      if (slot == 1) {
         IFluidHandlerItem cap = (IFluidHandlerItem)CapabilityUtil.getCapabilityHelper(stack, CapabilityFluidHandler.FLUID_HANDLER_ITEM_CAPABILITY).getValue();
         if (cap != null) {
            return cap.getTanks() > 0 && cap.getFluidInTank(1).getFluid() == Fluids.f_76191_;
         }
      }

      return false;
   }

   @Override
   public ItemStack insertItemForSlot(int slot, @Nonnull ItemStack stack, boolean simulate) {
      if (slot == 0) {
         IFluidHandlerItem cap = (IFluidHandlerItem)CapabilityUtil.getCapabilityHelper(stack, CapabilityFluidHandler.FLUID_HANDLER_ITEM_CAPABILITY).getValue();
         return cap != null && cap.getTanks() > 0 && cap.getFluidInTank(1).getFluid() == Biomass.STILL_FLUID ? null : stack;
      } else if (slot == 1) {
         IFluidHandlerItem cap = (IFluidHandlerItem)CapabilityUtil.getCapabilityHelper(stack, CapabilityFluidHandler.FLUID_HANDLER_ITEM_CAPABILITY).getValue();
         return cap != null && cap.getTanks() > 0 && cap.getFluidInTank(1).getFluid() == Fluids.f_76191_ ? null : stack;
      } else {
         return super.insertItemForSlot(slot, stack, simulate);
      }
   }

   @Nonnull
   @Override
   public <T> LazyOptional<T> getCapability(@Nonnull Capability<T> cap, @Nullable Direction side) {
      if (cap == CapabilityFluidHandler.FLUID_HANDLER_CAPABILITY) {
         if (side == null) {
            return LazyOptional.empty();
         } else {
            if (this.getBlock() instanceof IStateFacing facing) {
               Direction dir = facing.getDirection(this.m_58900_());
               if (dir.m_122427_() == side) {
                  return this.capabilities.get(3).cast();
               }

               if (dir.m_122428_() == side) {
                  return this.capabilities.get(4).cast();
               }
            }

            return LazyOptional.empty();
         }
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

   @Override
   public List<UpgradeType> getSupportedUpgrades() {
      return List.of(
         UpgradeType.OVERCLOCKER,
         UpgradeType.TRANSFORMER,
         UpgradeType.ENERGY_STORAGE,
         UpgradeType.EJECTOR,
         UpgradeType.PULLING,
         UpgradeType.FLUID_EJECTOR,
         UpgradeType.FLUID_PULLING,
         UpgradeType.REDSTONE_SIGNAL_INVERTER
      );
   }
}
