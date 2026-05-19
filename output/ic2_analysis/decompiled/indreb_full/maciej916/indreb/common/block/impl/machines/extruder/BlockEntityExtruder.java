package com.maciej916.indreb.common.block.impl.machines.extruder;

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
import com.maciej916.indreb.common.interfaces.entity.ITileSound;
import com.maciej916.indreb.common.network.ModNetworking;
import com.maciej916.indreb.common.network.packet.PacketExtruderRecipe;
import com.maciej916.indreb.common.recipe.impl.ExtrudingRecipe;
import com.maciej916.indreb.common.registries.ModBlockEntities;
import com.maciej916.indreb.common.registries.ModRecipeType;
import com.maciej916.indreb.common.registries.ModSounds;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;
import javax.annotation.Nonnull;
import javax.annotation.Nullable;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.item.crafting.RecipeType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.material.Fluids;
import net.minecraftforge.common.capabilities.Capability;
import net.minecraftforge.common.util.LazyOptional;
import net.minecraftforge.fluids.capability.CapabilityFluidHandler;
import net.minecraftforge.items.CapabilityItemHandler;
import net.minecraftforge.items.wrapper.RangedWrapper;

public class BlockEntityExtruder extends IndRebBlockEntity implements IEnergyBlock, ITileSound, IExpCollector, ISupportUpgrades {
   public static final int INPUT_SLOT = 0;
   public static final int OUTPUT_SLOT = 1;
   protected int cachedWater = 0;
   protected int cachedLava = 0;
   public FluidStorage waterStorage = new FluidStorage(8000, p -> p.getFluid() == Fluids.f_76193_);
   public FluidStorage lavaStorage = new FluidStorage(8000, p -> p.getFluid() == Fluids.f_76195_);
   public BlockEntityProgress progress = new BlockEntityProgress();
   protected int recipeIndex = 0;
   protected static List<ExtrudingRecipe> recipes;
   protected ExtrudingRecipe recipe;
   private boolean active = false;
   private final ArrayList<LazyOptional<?>> capabilities = new ArrayList<>(
      Arrays.asList(
         LazyOptional.of(this::getStackHandler),
         LazyOptional.of(() -> new RangedWrapper(this.getStackHandler(), 0, 1)),
         LazyOptional.of(() -> new RangedWrapper(this.getStackHandler(), 1, 2)),
         LazyOptional.of(() -> this.waterStorage),
         LazyOptional.of(() -> this.lavaStorage)
      )
   );

   public void setRecipe(int index) {
      if (this.f_58857_ != null) {
         this.recipe = Objects.requireNonNullElseGet(recipes, () -> this.f_58857_.m_7465_().m_44013_((RecipeType)ModRecipeType.EXTRUDING.get())).get(index);
         this.getStackHandler().setStackInSlot(0, this.recipe.m_8043_());
         this.progress.setBoth(-1.0F);
      }
   }

   public BlockEntityExtruder(BlockPos pWorldPosition, BlockState pBlockState) {
      super(ModBlockEntities.EXTRUDER, pWorldPosition, pBlockState);
      this.createEnergyStorage(0, (Integer)ServerConfig.extruder_energy_capacity.get(), EnergyType.RECEIVE, EnergyTier.BASIC);
   }

   @Override
   public ArrayList<IndRebSlot> addInventorySlot(ArrayList<IndRebSlot> slots) {
      slots.add(new IndRebSlot(0, 80, 59, InventorySlotType.DISABLED, GuiSlotType.NORMAL, 79, 58));
      slots.add(new IndRebSlot(1, 121, 35, InventorySlotType.OUTPUT, GuiSlotType.LARGE, 116, 30));
      return super.addInventorySlot(slots);
   }

   @Override
   public ArrayList<IElectricSlot> addBatterySlot(ArrayList<IElectricSlot> slots) {
      slots.add(new SlotBattery(0, 152, 62, false));
      return super.addBatterySlot(slots);
   }

   public SoundEvent getSoundEvent() {
      return ModSounds.EXTRACTOR;
   }

   @Override
   public boolean isItemValidForSlot(int slot, @Nonnull ItemStack stack) {
      return slot != 0 && slot != 1 ? super.isItemValidForSlot(slot, stack) : false;
   }

   public Runnable prevRecipe() {
      return () -> ModNetworking.INSTANCE.sendToServer(new PacketExtruderRecipe(this.m_58899_(), false));
   }

   public Runnable nextRecipe() {
      return () -> ModNetworking.INSTANCE.sendToServer(new PacketExtruderRecipe(this.m_58899_(), true));
   }

   public void initRecipes() {
      recipes = Objects.requireNonNull(this.m_58904_()).m_7465_().m_44013_((RecipeType)ModRecipeType.EXTRUDING.get());
   }

   public void changeRecipe(boolean next) {
      if (recipes != null) {
         int newIndex = this.recipeIndex + (next ? 1 : -1);
         if (newIndex > recipes.size() - 1) {
            newIndex = 0;
         }

         if (newIndex < 0) {
            newIndex = recipes.size() - 1;
         }

         this.setRecipe(newIndex);
         this.recipeIndex = newIndex;
         this.progress.setBoth(-1.0F);
         this.setActive(false);
         this.updateBlockState();
      }
   }

   @Override
   public void tickOperate(BlockState state) {
      this.active = false;
      this.getEnergyStorage().updateConsumed(0);
      if (recipes == null) {
         this.initRecipes();
      }

      if (this.cachedWater != this.waterStorage.getFluid().getAmount() || this.cachedLava != this.lavaStorage.getFluid().getAmount()) {
         this.cachedWater = this.waterStorage.getFluid().getAmount();
         this.cachedLava = this.lavaStorage.getFluid().getAmount();
         this.updateBlockState();
      }

      if (this.recipe == null && recipes != null) {
         this.setRecipe(0);
         this.updateBlockState();
      }

      ItemStack outputStack = this.getStackHandler().getStackInSlot(1);
      if (this.recipe != null) {
         this.progress.setProgressMax(this.getSpeedFactor() * (float)this.recipe.getDuration());
         int energyCost = (int)((float)this.recipe.getPowerCost() * this.getEnergyUsageFactor());
         if (this.getEnergyStorage().consumeEnergy(energyCost, true) == energyCost
            && this.recipe.m_8043_().m_41613_() + outputStack.m_41613_() <= outputStack.m_41741_()
            && (outputStack.m_41619_() || outputStack.m_41720_() == this.recipe.m_8043_().m_41720_())
            && !this.waterStorage.getFluid().isEmpty()
            && !this.lavaStorage.getFluid().isEmpty()
            && this.lavaStorage.takeFluid(this.recipe.getWaterCost(), true) == this.recipe.getWaterCost()
            && this.lavaStorage.takeFluid(this.recipe.getLavaCost(), true) == this.recipe.getLavaCost()) {
            if (this.progress.getProgress() == -1.0F) {
               this.progress.setData(0.0F, (float)this.recipe.getDuration());
            }

            this.getEnergyStorage().consumeEnergy(energyCost, false);
            this.getEnergyStorage().updateConsumed(energyCost);
            this.progress.incProgress(1.0F);
            this.active = true;
         }
      }

      if (this.progress.getProgress() > 0.0F && this.progress.getProgress() >= this.progress.getProgressMax()) {
         this.progress.setBoth(-1.0F);
         this.setRecipeUsed(this.recipe);
         if (this.recipe.getWaterCost() > 0) {
            this.waterStorage.takeFluid(this.recipe.getWaterCost(), false);
         }

         if (this.recipe.getLavaCost() > 0) {
            this.lavaStorage.takeFluid(this.recipe.getLavaCost(), false);
         }

         if (outputStack.m_41619_()) {
            this.getStackHandler().setStackInSlot(1, this.recipe.m_8043_().m_41777_());
         } else {
            this.getStackHandler().getStackInSlot(1).m_41769_(this.recipe.m_8043_().m_41613_());
         }
      }

      this.setActive(this.active);
      if (this.progress.changed()) {
         super.updateBlockState();
      }
   }

   @Override
   public void m_142466_(CompoundTag tag) {
      super.m_142466_(tag);
      this.cachedWater = tag.m_128451_("cachedWater");
      this.cachedLava = tag.m_128451_("cachedLava");
      this.lavaStorage.readFromNBT(tag.m_128469_("lava_storage"));
      this.waterStorage.readFromNBT(tag.m_128469_("water_storage"));
      this.active = tag.m_128471_("active");
      this.progress.deserializeNBT(tag.m_128469_("progress"));
   }

   @Override
   public CompoundTag save(CompoundTag tag) {
      tag.m_128405_("cachedWater", this.cachedWater);
      tag.m_128405_("cachedLava", this.cachedLava);
      tag.m_128365_("lava_storage", this.lavaStorage.writeToNBT(tag.m_128469_("lava_storage")));
      tag.m_128365_("water_storage", this.waterStorage.writeToNBT(tag.m_128469_("water_storage")));
      tag.m_128379_("active", this.active);
      tag.m_128365_("progress", this.progress.serializeNBT());
      return super.save(tag);
   }

   @Override
   public float getExperience(Recipe<?> recipe) {
      return ((ExtrudingRecipe)recipe).getExperience();
   }

   @Override
   public boolean canReceiveEnergyDir(Direction side) {
      return true;
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
