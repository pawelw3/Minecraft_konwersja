package dev.ftb.mods.ftbic.block.entity.storage;

import dev.ftb.mods.ftbic.FTBICConfig;
import dev.ftb.mods.ftbic.block.ElectricBlockInstance;
import dev.ftb.mods.ftbic.block.entity.generator.GeneratorBlockEntity;
import dev.ftb.mods.ftbic.block.entity.machine.BatteryInventory;
import dev.ftb.mods.ftbic.screen.BatteryBoxMenu;
import dev.ftb.mods.ftbic.util.EnergyItemHandler;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraftforge.common.capabilities.Capability;
import net.minecraftforge.common.util.LazyOptional;
import net.minecraftforge.items.CapabilityItemHandler;
import net.minecraftforge.items.IItemHandler;
import net.minecraftforge.items.ItemHandlerHelper;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;

public class BatteryBoxBlockEntity extends GeneratorBlockEntity {
   public final BatteryInventory dischargeBatteryInventory = new BatteryInventory(this, false);
   private LazyOptional<IItemHandler> dischargeBatteryInventoryOptional;
   private LazyOptional<IItemHandler> chargeBatteryInventoryOptional;

   public BatteryBoxBlockEntity(ElectricBlockInstance type, BlockPos pos, BlockState state) {
      super(type, pos, state);
   }

   @Override
   public void initProperties() {
      super.initProperties();
      this.maxEnergyOutputTransfer = this.maxEnergyOutput;
   }

   @Override
   public void writeData(CompoundTag tag) {
      super.writeData(tag);
      if (!this.dischargeBatteryInventory.getStackInSlot(0).m_41619_()) {
         tag.m_128365_("DischargeBattery", this.dischargeBatteryInventory.getStackInSlot(0).serializeNBT());
      }
   }

   @Override
   public void readData(CompoundTag tag) {
      super.readData(tag);
      if (tag.m_128441_("DischargeBattery")) {
         this.dischargeBatteryInventory.loadItem(ItemStack.m_41712_(tag.m_128469_("DischargeBattery")));
      } else {
         this.dischargeBatteryInventory.loadItem(ItemStack.f_41583_);
      }
   }

   @Override
   public void onBroken(Level level, BlockPos pos) {
      super.onBroken(level, pos);
      Block.m_49840_(level, pos, this.dischargeBatteryInventory.getStackInSlot(0));
   }

   @Override
   public boolean isValidEnergyOutputSide(Direction direction) {
      return direction == this.getFacing(Direction.NORTH);
   }

   @Override
   public boolean isValidEnergyInputSide(Direction direction) {
      return direction != this.getFacing(Direction.NORTH);
   }

   @Override
   public void handleGeneration() {
      if (!this.isBurnt() && !this.f_58857_.m_5776_() && this.energy < this.energyCapacity) {
         ItemStack battery = this.dischargeBatteryInventory.getStackInSlot(0);
         if (!battery.m_41619_() && battery.m_41720_() instanceof EnergyItemHandler item) {
            double transfer = item.isCreativeEnergyItem()
               ? Double.POSITIVE_INFINITY
               : this.maxInputEnergy * (Double)FTBICConfig.MACHINES.ITEM_TRANSFER_EFFICIENCY.get();
            double e = item.extractEnergy(battery, Math.min(this.energyCapacity - this.energy, transfer), false);
            if (e > 0.0) {
               this.energy += e;
               if (battery.m_41619_()) {
                  this.dischargeBatteryInventory.setStackInSlot(0, ItemStack.f_41583_);
               }

               this.m_6596_();
            }
         }
      }
   }

   @Override
   public InteractionResult rightClick(Player player, InteractionHand hand, BlockHitResult hit) {
      if (!this.f_58857_.m_5776_()) {
         this.openMenu((ServerPlayer)player, (id, inventory) -> new BatteryBoxMenu(id, inventory, this));
      }

      return InteractionResult.SUCCESS;
   }

   @Override
   public int getSlots() {
      return 2;
   }

   @NotNull
   @Override
   public ItemStack getStackInSlot(int slot) {
      return switch (slot) {
         case 0 -> this.chargeBatteryInventory.getStackInSlot(0);
         case 1 -> this.dischargeBatteryInventory.getStackInSlot(0);
         default -> throw new RuntimeException("Slot " + slot + " not in valid range - [0," + this.getSlots() + ")");
      };
   }

   @Override
   public void setStackInSlot(int slot, ItemStack stack) {
      ItemStack prev;
      switch (slot) {
         case 0:
            prev = this.chargeBatteryInventory.getStackInSlot(0);
            this.chargeBatteryInventory.setStackInSlot(0, stack);
            break;
         case 1:
            prev = this.dischargeBatteryInventory.getStackInSlot(0);
            this.dischargeBatteryInventory.setStackInSlot(0, stack);
            break;
         default:
            throw new RuntimeException("Slot " + slot + " not in valid range - [0," + this.getSlots() + ")");
      }

      this.inventoryChanged(slot, prev);
   }

   @NotNull
   @Override
   public ItemStack insertItem(int slot, @NotNull ItemStack stack, boolean simulate) {
      if (slot < this.getSlots() && !stack.m_41619_() && this.isItemValid(slot, stack)) {
         ItemStack existing = this.getStackInSlot(slot);
         int limit = Math.min(this.getSlotLimit(slot), stack.m_41741_());
         if (!existing.m_41619_()) {
            if (!ItemHandlerHelper.canItemStacksStack(stack, existing)) {
               return stack;
            }

            limit -= existing.m_41613_();
         }

         if (limit <= 0) {
            return stack;
         } else {
            boolean reachedLimit = stack.m_41613_() > limit;
            if (!simulate) {
               if (existing.m_41619_()) {
                  ItemStack prev = this.getStackInSlot(slot);
                  switch (slot) {
                     case 0:
                        this.chargeBatteryInventory.setStackInSlot(0, reachedLimit ? ItemHandlerHelper.copyStackWithSize(stack, limit) : stack);
                        break;
                     case 1:
                        this.dischargeBatteryInventory.setStackInSlot(0, reachedLimit ? ItemHandlerHelper.copyStackWithSize(stack, limit) : stack);
                  }

                  this.inventoryChanged(slot, prev);
               } else {
                  ItemStack prev = existing.m_41777_();
                  existing.m_41769_(reachedLimit ? limit : stack.m_41613_());
                  this.inventoryChanged(slot, prev);
               }
            }

            return reachedLimit ? ItemHandlerHelper.copyStackWithSize(stack, stack.m_41613_() - limit) : ItemStack.f_41583_;
         }
      } else {
         return stack;
      }
   }

   @NotNull
   @Override
   public ItemStack extractItem(int slot, int amount, boolean simulate) {
      if (slot >= 0 && slot <= 1) {
         BatteryInventory batteryInv = slot == 0 ? this.chargeBatteryInventory : this.dischargeBatteryInventory;
         ItemStack existing = batteryInv.getStackInSlot(0);
         if (existing.m_41619_()) {
            return ItemStack.f_41583_;
         } else {
            int toExtract = Math.min(amount, existing.m_41741_());
            if (existing.m_41613_() <= toExtract) {
               if (!simulate) {
                  batteryInv.setStackInSlot(0, ItemStack.f_41583_);
                  this.inventoryChanged(slot, existing);
                  return existing;
               } else {
                  return existing.m_41777_();
               }
            } else {
               if (!simulate) {
                  batteryInv.setStackInSlot(0, ItemHandlerHelper.copyStackWithSize(existing, existing.m_41613_() - toExtract));
                  this.inventoryChanged(slot, existing);
               }

               return ItemHandlerHelper.copyStackWithSize(existing, toExtract);
            }
         }
      } else {
         return ItemStack.f_41583_;
      }
   }

   @Override
   public int getSlotLimit(int slot) {
      return 64;
   }

   @Override
   public boolean isItemValid(int slot, @NotNull ItemStack stack) {
      return slot == 0 && this.chargeBatteryInventory.isItemValid(0, stack) || slot == 1 && this.dischargeBatteryInventory.isItemValid(0, stack);
   }

   public LazyOptional<?> getDischargeBatteryInventoryOptional() {
      if (this.dischargeBatteryInventoryOptional == null) {
         this.dischargeBatteryInventoryOptional = LazyOptional.of(() -> this.dischargeBatteryInventory);
      }

      return this.dischargeBatteryInventoryOptional;
   }

   public LazyOptional<?> getChargeBatteryInventoryOptional() {
      if (this.chargeBatteryInventoryOptional == null) {
         this.chargeBatteryInventoryOptional = LazyOptional.of(() -> this.chargeBatteryInventory);
      }

      return this.chargeBatteryInventoryOptional;
   }

   @Override
   public void invalidateCaps() {
      super.invalidateCaps();
      if (this.dischargeBatteryInventoryOptional != null) {
         this.dischargeBatteryInventoryOptional.invalidate();
         this.dischargeBatteryInventoryOptional = null;
      }

      if (this.chargeBatteryInventoryOptional != null) {
         this.chargeBatteryInventoryOptional.invalidate();
         this.chargeBatteryInventoryOptional = null;
      }
   }

   @NotNull
   @Override
   public <T> LazyOptional<T> getCapability(@NotNull Capability<T> cap, @Nullable Direction side) {
      if (cap == CapabilityItemHandler.ITEM_HANDLER_CAPABILITY) {
         return side == Direction.UP ? this.getDischargeBatteryInventoryOptional().cast() : this.getChargeBatteryInventoryOptional().cast();
      } else {
         return super.getCapability(cap, side);
      }
   }
}
