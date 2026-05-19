package com.maciej916.indreb.common.block.impl.machines.alloy_smelter;

import com.maciej916.indreb.common.config.ServerConfig;
import com.maciej916.indreb.common.energy.interfaces.IEnergyBlock;
import com.maciej916.indreb.common.entity.block.BlockEntityProgress;
import com.maciej916.indreb.common.entity.block.IndRebBlockEntity;
import com.maciej916.indreb.common.entity.slot.IndRebSlot;
import com.maciej916.indreb.common.entity.slot.SlotBattery;
import com.maciej916.indreb.common.enums.EnergyTier;
import com.maciej916.indreb.common.enums.EnergyType;
import com.maciej916.indreb.common.enums.GuiSlotType;
import com.maciej916.indreb.common.enums.InventorySlotType;
import com.maciej916.indreb.common.enums.UpgradeType;
import com.maciej916.indreb.common.interfaces.entity.IElectricSlot;
import com.maciej916.indreb.common.interfaces.entity.IExpCollector;
import com.maciej916.indreb.common.interfaces.entity.ISupportUpgrades;
import com.maciej916.indreb.common.recipe.impl.AlloySmeltingRecipe;
import com.maciej916.indreb.common.registries.ModBlockEntities;
import com.maciej916.indreb.common.registries.ModRecipeType;
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
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.item.crafting.RecipeType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.common.capabilities.Capability;
import net.minecraftforge.common.util.LazyOptional;
import net.minecraftforge.items.CapabilityItemHandler;
import net.minecraftforge.items.wrapper.RangedWrapper;

public class BlockEntityAlloySmelter extends IndRebBlockEntity implements IEnergyBlock, IExpCollector, ISupportUpgrades {
   public static final int INPUT_SLOT_0 = 0;
   public static final int INPUT_SLOT_1 = 1;
   public static final int INPUT_SLOT_2 = 2;
   public static final int OUTPUT_SLOT = 3;
   public BlockEntityProgress progress = new BlockEntityProgress();
   public BlockEntityProgress heatLevel = new BlockEntityProgress(0, 100);
   private boolean active = false;
   private ItemStack resultStack = ItemStack.f_41583_;
   protected AlloySmeltingRecipe recipe;
   private int energyCostPerTick = 0;
   private int duration = 0;
   private ItemStack cachedInputStack1 = ItemStack.f_41583_;
   private ItemStack cachedInputStack2 = ItemStack.f_41583_;
   private ItemStack cachedInputStack3 = ItemStack.f_41583_;
   private ItemStack cachedOutput = ItemStack.f_41583_;
   private boolean cachedWork;
   private final ArrayList<LazyOptional<?>> capabilities = new ArrayList<>(
      Arrays.asList(
         LazyOptional.of(this::getStackHandler),
         LazyOptional.of(() -> new RangedWrapper(this.getStackHandler(), 0, 3)),
         LazyOptional.of(() -> new RangedWrapper(this.getStackHandler(), 3, 4))
      )
   );

   public BlockEntityAlloySmelter(BlockPos pWorldPosition, BlockState pBlockState) {
      super(ModBlockEntities.ALLOY_SMELTER, pWorldPosition, pBlockState);
      this.createEnergyStorage(0, (Integer)ServerConfig.alloy_smelter_energy_capacity.get(), EnergyType.RECEIVE, EnergyTier.STANDARD);
   }

   @Override
   public ArrayList<IndRebSlot> addInventorySlot(ArrayList<IndRebSlot> slots) {
      slots.add(new IndRebSlot(0, 16, 33, InventorySlotType.INPUT, GuiSlotType.NORMAL, 15, 32));
      slots.add(new IndRebSlot(1, 37, 21, InventorySlotType.INPUT, GuiSlotType.NORMAL, 36, 20));
      slots.add(new IndRebSlot(2, 58, 33, InventorySlotType.INPUT, GuiSlotType.NORMAL, 57, 32));
      slots.add(new IndRebSlot(3, 118, 33, InventorySlotType.OUTPUT, GuiSlotType.LARGE, 113, 28));
      return super.addInventorySlot(slots);
   }

   @Override
   public ArrayList<IElectricSlot> addBatterySlot(ArrayList<IElectricSlot> slots) {
      slots.add(new SlotBattery(0, 152, 62, false));
      return super.addBatterySlot(slots);
   }

   protected Optional<AlloySmeltingRecipe> getRecipe(ItemStack... input) {
      return this.f_58857_ == null
         ? Optional.empty()
         : this.f_58857_.m_7465_().m_44015_((RecipeType)ModRecipeType.ALLOY_SMELTING.get(), new SimpleContainer(input), this.f_58857_);
   }

   protected ItemStack getRecipeResult(ItemStack... stack) {
      return this.recipe.m_5874_(new SimpleContainer(stack));
   }

   private boolean isValidInput(ItemStack... stack) {
      return this.getRecipe(stack).isPresent();
   }

   private boolean canWork(ItemStack inputStack0, ItemStack inputStack1, ItemStack inputStack2, ItemStack outputStack, ItemStack resultStack) {
      return this.isValidInput(inputStack0, inputStack1, inputStack2)
         && (
            outputStack.m_41619_()
               || resultStack.m_41613_() + outputStack.m_41613_() <= outputStack.m_41741_() && resultStack.m_41720_() == outputStack.m_41720_()
         );
   }

   @Override
   public void tickOperate(BlockState state) {
      this.active = false;
      this.getEnergyStorage().updateConsumed(0);
      ItemStack inputStack0 = this.getStackHandler().getStackInSlot(0);
      ItemStack inputStack1 = this.getStackHandler().getStackInSlot(1);
      ItemStack inputStack2 = this.getStackHandler().getStackInSlot(2);
      ItemStack outputStack = this.getStackHandler().getStackInSlot(3);
      if (this.cachedInputStack1 != inputStack0
         || this.cachedInputStack2 != inputStack1
         || this.cachedInputStack3 != inputStack2
         || this.cachedOutput != outputStack) {
         this.cachedInputStack1 = inputStack0.m_41777_();
         this.cachedInputStack2 = inputStack1.m_41777_();
         this.cachedInputStack3 = inputStack2.m_41777_();
         this.cachedOutput = outputStack.m_41777_();
         if (this.getRecipe(inputStack0, inputStack1, inputStack2).isPresent()) {
            this.recipe = this.getRecipe(inputStack0, inputStack1, inputStack2).get();
            this.resultStack = this.getRecipeResult(inputStack0, inputStack1, inputStack2);
            this.energyCostPerTick = this.recipe.getPowerCost();
            this.duration = this.recipe.getDuration();
         } else {
            this.recipe = null;
         }

         this.cachedWork = false;
      }

      if (this.recipe != null && (this.cachedWork || this.canWork(inputStack0, inputStack1, inputStack2, outputStack, this.resultStack))) {
         if (this.progress.getProgress() == -1.0F) {
            this.progress.setData(0.0F, (float)this.duration);
         }

         this.progress.setProgressMax(this.getSpeedFactor() * (float)this.duration);
         int energyCost = (int)((float)this.energyCostPerTick * this.getEnergyUsageFactor());
         if (this.getEnergyStorage().consumeEnergy(energyCost, true) == energyCost
            && this.progress.getProgress() <= this.progress.getProgressMax()
            && this.progress.getProgress() <= this.progress.getProgressMax()) {
            this.active = true;
            this.progress.incProgress(1.0F + this.heatLevel.getPercentProgress() / 100.0F);
            this.getEnergyStorage().consumeEnergy(energyCost, false);
            this.getEnergyStorage().updateConsumed(energyCost);
         }

         if (this.progress.getProgress() >= this.progress.getProgressMax()) {
            if (outputStack.m_41619_()) {
               this.getStackHandler().setStackInSlot(3, this.resultStack.m_41777_());
            } else {
               outputStack.m_41769_(this.resultStack.m_41613_());
               this.getStackHandler().setStackInSlot(3, outputStack.m_41777_());
            }

            int cost0 = this.recipe.getIngredientCost(inputStack0);
            if (cost0 > 0) {
               inputStack0.m_41774_(cost0);
               this.getStackHandler().setStackInSlot(0, inputStack0.m_41777_());
            }

            int cost1 = this.recipe.getIngredientCost(inputStack1);
            if (cost1 > 0) {
               inputStack1.m_41774_(cost1);
               this.getStackHandler().setStackInSlot(1, inputStack1.m_41777_());
            }

            int cost2 = this.recipe.getIngredientCost(inputStack2);
            if (cost2 > 0) {
               inputStack2.m_41774_(cost2);
               this.getStackHandler().setStackInSlot(2, inputStack2.m_41777_());
            }

            this.setRecipeUsed(this.recipe);
            this.progress.setBoth(-1.0F);
         }
      } else {
         this.progress.setBoth(-1.0F);
      }

      if ((
            this.getRedstonePower() <= 0
               || this.getEnergyStorage().consumeEnergy((Integer)ServerConfig.alloy_smelter_heat_cost.get(), true)
                  < (Integer)ServerConfig.alloy_smelter_heat_cost.get()
         )
         && !this.active) {
         if (this.heatLevel.getProgress() > 0.0F && this.tickCounter == 20) {
            this.heatLevel.decProgress(Math.min(this.heatLevel.getProgress(), 1.0F));
         }
      } else if (this.heatLevel.getProgress() < 100.0F && this.tickCounter == 20) {
         this.heatLevel.incProgress(0.2F);
         if (!this.active) {
            this.getEnergyStorage().consumeEnergy((Integer)ServerConfig.alloy_smelter_heat_cost.get(), false);
         }
      }

      this.setActive(this.active);
      if (this.heatLevel.changed() || this.progress.changed()) {
         super.updateBlockState();
      }
   }

   @Override
   public boolean isItemValidForSlot(int slot, @Nonnull ItemStack stack) {
      if (slot == 0) {
         return this.isValidInput(stack);
      } else if (slot == 1) {
         return this.isValidInput(stack);
      } else {
         return slot == 2 ? this.isValidInput(stack) : false;
      }
   }

   @Override
   public ItemStack insertItemForSlot(int slot, @Nonnull ItemStack stack, boolean simulate) {
      return (slot == 0 || slot == 1 || slot == 2) && !this.isValidInput(stack) ? stack : super.insertItemForSlot(slot, stack, simulate);
   }

   @Override
   public void m_142466_(CompoundTag tag) {
      super.m_142466_(tag);
      this.active = tag.m_128471_("active");
      this.progress.deserializeNBT(tag.m_128469_("progress"));
      this.heatLevel.deserializeNBT(tag.m_128469_("heatLevel"));
   }

   @Override
   public CompoundTag save(CompoundTag tag) {
      tag.m_128379_("active", this.active);
      tag.m_128365_("progress", this.progress.serializeNBT());
      tag.m_128365_("heatLevel", this.heatLevel.serializeNBT());
      return super.save(tag);
   }

   @Override
   public float getExperience(Recipe<?> recipe) {
      return ((AlloySmeltingRecipe)recipe).getExperience();
   }

   @Override
   public boolean canReceiveEnergyDir(Direction side) {
      return true;
   }

   @Nonnull
   @Override
   public <T> LazyOptional<T> getCapability(@Nonnull Capability<T> cap, @Nullable Direction side) {
      if (cap == CapabilityItemHandler.ITEM_HANDLER_CAPABILITY) {
         return switch (side) {
            case UP -> this.capabilities.get(1).cast();
            case DOWN -> this.capabilities.get(2).cast();
            default -> this.capabilities.get(0).cast();
         };
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
         UpgradeType.REDSTONE_SIGNAL_INVERTER
      );
   }
}
