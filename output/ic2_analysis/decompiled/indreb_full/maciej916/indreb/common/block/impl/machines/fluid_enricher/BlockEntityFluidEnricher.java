package com.maciej916.indreb.common.block.impl.machines.fluid_enricher;

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
import com.maciej916.indreb.common.interfaces.block.IStateFacing;
import com.maciej916.indreb.common.interfaces.entity.IElectricSlot;
import com.maciej916.indreb.common.interfaces.entity.IExpCollector;
import com.maciej916.indreb.common.interfaces.entity.ISupportUpgrades;
import com.maciej916.indreb.common.recipe.impl.FluidEnrichingRecipe;
import com.maciej916.indreb.common.registries.ModBlockEntities;
import com.maciej916.indreb.common.registries.ModRecipeType;
import com.maciej916.indreb.common.util.BlockEntityUtil;
import com.maciej916.indreb.common.util.CapabilityUtil;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import javax.annotation.Nonnull;
import javax.annotation.Nullable;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.item.crafting.RecipeType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.material.Fluids;
import net.minecraftforge.common.capabilities.Capability;
import net.minecraftforge.common.util.LazyOptional;
import net.minecraftforge.fluids.capability.CapabilityFluidHandler;
import net.minecraftforge.fluids.capability.IFluidHandlerItem;
import net.minecraftforge.fluids.capability.IFluidHandler.FluidAction;
import net.minecraftforge.items.CapabilityItemHandler;
import net.minecraftforge.items.wrapper.RangedWrapper;

public class BlockEntityFluidEnricher extends IndRebBlockEntity implements IEnergyBlock, IExpCollector, ISupportUpgrades {
   public static final int INPUT_SLOT = 0;
   public static final int DRAIN_BUCKET_UP = 1;
   public static final int DRAIN_BUCKET_DOWN = 2;
   public FluidStorage fluidInputStorage = new FluidStorage(8000);
   public FluidStorage fluidOutputStorage = new FluidStorage(8000);
   private int cachedInput = 0;
   private int cachedOutput = 0;
   public BlockEntityProgress progressDrain = new BlockEntityProgress(0, 1);
   private boolean active = false;
   public BlockEntityProgress progress = new BlockEntityProgress();
   private FluidEnrichingRecipe recipe;
   private ItemStack cachedInputStack = ItemStack.f_41583_;
   private final ArrayList<LazyOptional<?>> capabilities = new ArrayList<>(
      Arrays.asList(
         LazyOptional.of(this::getStackHandler),
         LazyOptional.of(() -> new RangedWrapper(this.getStackHandler(), 0, 2)),
         LazyOptional.of(() -> new RangedWrapper(this.getStackHandler(), 2, 3)),
         LazyOptional.of(() -> this.fluidInputStorage),
         LazyOptional.of(() -> this.fluidOutputStorage)
      )
   );

   public BlockEntityFluidEnricher(BlockPos pWorldPosition, BlockState pBlockState) {
      super(ModBlockEntities.FLUID_ENRICHER, pWorldPosition, pBlockState);
      this.createEnergyStorage(0, (Integer)ServerConfig.fluid_enricher_energy_capacity.get(), EnergyType.RECEIVE, EnergyTier.BASIC);
   }

   @Override
   public ArrayList<IndRebSlot> addInventorySlot(ArrayList<IndRebSlot> slots) {
      slots.add(new IndRebSlot(0, 13, 35, InventorySlotType.INPUT, GuiSlotType.NORMAL, 12, 34));
      slots.add(new IndRebSlot(1, 127, 19, InventorySlotType.INPUT, GuiSlotType.NORMAL, 126, 18));
      slots.add(new IndRebSlot(2, 127, 50, InventorySlotType.OUTPUT, GuiSlotType.NORMAL, 126, 49));
      return super.addInventorySlot(slots);
   }

   @Override
   public ArrayList<IElectricSlot> addBatterySlot(ArrayList<IElectricSlot> slots) {
      slots.add(new SlotBattery(0, 152, 62, false));
      return super.addBatterySlot(slots);
   }

   protected Optional<FluidEnrichingRecipe> getRawRecipe(ItemStack input) {
      return this.f_58857_.m_7465_().m_44015_((RecipeType)ModRecipeType.FLUID_ENRICHING.get(), new SimpleContainer(new ItemStack[]{input}), this.f_58857_);
   }

   protected Optional<FluidEnrichingRecipe> getRecipe(ItemStack input) {
      for (FluidEnrichingRecipe recipe : this.f_58857_.m_7465_().m_44013_((RecipeType)ModRecipeType.FLUID_ENRICHING.get())) {
         if (recipe.m_5818_(new SimpleContainer(new ItemStack[]{input}), this.f_58857_)
            && recipe.getFluidInput().getFluid() == this.fluidInputStorage.getFluid().getFluid()) {
            return Optional.of(recipe);
         }
      }

      return Optional.empty();
   }

   protected ItemStack getRecipeResult(ItemStack stack) {
      return this.recipe.m_5874_(new SimpleContainer(new ItemStack[]{stack}));
   }

   private boolean isValidInput(ItemStack stack) {
      return stack.m_41619_() ? false : this.getRawRecipe(stack).isPresent();
   }

   private boolean canWork(ItemStack inputStack) {
      return inputStack.m_41613_() >= this.recipe.getIngredientCount()
         && (this.recipe.getResult().getFluid() == this.fluidOutputStorage.getFluid().getFluid() || this.fluidOutputStorage.getFluid().isEmpty())
         && this.fluidOutputStorage.fillFluid(this.recipe.getResult(), true) == this.recipe.getResult().getAmount();
   }

   @Override
   public void tickOperate(BlockState state) {
      this.active = false;
      boolean updateState = false;
      this.getEnergyStorage().updateConsumed(0);
      ItemStack inputStack = this.getStackHandler().getStackInSlot(0);
      ItemStack drainBucketUp = this.getStackHandler().getStackInSlot(1);
      ItemStack drainBucketDown = this.getStackHandler().getStackInSlot(2);
      if (this.cachedInput != this.fluidInputStorage.getFluidAmount()) {
         this.cachedInput = this.fluidInputStorage.getFluidAmount();
         updateState = true;
      }

      if (this.cachedOutput != this.fluidOutputStorage.getFluidAmount()) {
         this.cachedOutput = this.fluidOutputStorage.getFluidAmount();
         updateState = true;
      }

      if (this.progressDrain.getProgress() == 0.0F) {
         boolean drained = BlockEntityUtil.drainTank(drainBucketUp, drainBucketDown, this.fluidOutputStorage, this.getStackHandler(), 1, 2);
         if (drained) {
            this.progressDrain.setProgress(1.0F);
         }
      } else {
         this.progressDrain.setProgress(0.0F);
      }

      if (this.progressDrain.changed()) {
         updateState = true;
      }

      if (this.cachedInputStack.m_41720_() != inputStack.m_41720_()) {
         this.cachedInputStack = inputStack.m_41777_();
         if (inputStack.m_41720_() != Items.f_41852_ && this.getRecipe(inputStack).isPresent()) {
            this.recipe = this.getRecipe(inputStack).get();
         } else {
            this.recipe = null;
         }
      }

      if (this.fluidInputStorage.getFluidAmount() >= 1000) {
         if (this.recipe != null) {
            if (this.progress.getProgress() == -1.0F) {
               this.progress.setData(0.0F, (float)this.recipe.getDuration());
            }

            this.progress.setProgressMax(this.getSpeedFactor() * (float)this.recipe.getDuration());
            int energyCost = (int)((float)this.recipe.getPowerCost() * this.getEnergyUsageFactor());
            if (this.canWork(inputStack)) {
               if (this.getEnergyStorage().consumeEnergy(energyCost, true) == energyCost && this.progress.getProgress() <= this.progress.getProgressMax()) {
                  this.active = true;
                  this.progress.incProgress(1.0F);
                  this.getEnergyStorage().consumeEnergy(energyCost, false);
                  this.getEnergyStorage().updateConsumed(energyCost);
               }

               if (this.progress.getProgress() >= this.progress.getProgressMax()) {
                  inputStack.m_41774_(1);
                  this.getStackHandler().setStackInSlot(0, inputStack.m_41777_());
                  this.fluidInputStorage.drain(this.recipe.getFluidInput().getAmount(), FluidAction.EXECUTE);
                  this.fluidOutputStorage.fillFluid(this.recipe.getResult(), false);
                  this.progress.setBoth(-1.0F);
               }
            }
         }
      } else {
         this.progress.setBoth(-1.0F);
      }

      if (this.progress.changed()) {
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
      this.active = tag.m_128471_("active");
      this.progressDrain.deserializeNBT(tag.m_128469_("progressDrain"));
      this.progress.deserializeNBT(tag.m_128469_("progress"));
   }

   @Override
   public CompoundTag save(CompoundTag tag) {
      tag.m_128365_("fluidInputStorage", this.fluidInputStorage.writeToNBT(tag.m_128469_("fluidInputStorage")));
      tag.m_128365_("fluidOutputStorage", this.fluidOutputStorage.writeToNBT(tag.m_128469_("fluidOutputStorage")));
      tag.m_128379_("active", this.active);
      tag.m_128365_("progressDrain", this.progressDrain.serializeNBT());
      tag.m_128365_("progress", this.progress.serializeNBT());
      return super.save(tag);
   }

   @Override
   public boolean canReceiveEnergyDir(Direction side) {
      return true;
   }

   @Override
   public float getExperience(Recipe<?> recipe) {
      return ((FluidEnrichingRecipe)recipe).getExperience();
   }

   @Override
   public boolean isItemValidForSlot(int slot, @Nonnull ItemStack stack) {
      if (slot == 0) {
         return this.isValidInput(stack);
      } else {
         if (slot == 1) {
            IFluidHandlerItem cap = (IFluidHandlerItem)CapabilityUtil.getCapabilityHelper(stack, CapabilityFluidHandler.FLUID_HANDLER_ITEM_CAPABILITY)
               .getValue();
            if (cap != null) {
               return cap.getTanks() > 0 && cap.getFluidInTank(1).getFluid() == Fluids.f_76191_
                  || cap.getFluidInTank(1).getFluid() == this.fluidOutputStorage.getFluid().getFluid()
                     && cap.getFluidInTank(1).getAmount() < cap.getTankCapacity(1);
            }
         }

         return false;
      }
   }

   @Override
   public ItemStack insertItemForSlot(int slot, @Nonnull ItemStack stack, boolean simulate) {
      if (slot == 0 && !this.isValidInput(stack)) {
         return stack;
      } else if (slot != 1) {
         return super.insertItemForSlot(slot, stack, simulate);
      } else {
         IFluidHandlerItem cap = (IFluidHandlerItem)CapabilityUtil.getCapabilityHelper(stack, CapabilityFluidHandler.FLUID_HANDLER_ITEM_CAPABILITY).getValue();
         return cap == null
               || (cap.getTanks() <= 0 || cap.getFluidInTank(1).getFluid() != Fluids.f_76191_)
                  && (
                     cap.getFluidInTank(1).getFluid() != this.fluidOutputStorage.getFluid().getFluid()
                        || cap.getFluidInTank(1).getAmount() >= cap.getTankCapacity(1)
                  )
            ? stack
            : null;
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
         UpgradeType.REDSTONE_SIGNAL_INVERTER,
         UpgradeType.FLUID_PULLING,
         UpgradeType.FLUID_EJECTOR
      );
   }
}
