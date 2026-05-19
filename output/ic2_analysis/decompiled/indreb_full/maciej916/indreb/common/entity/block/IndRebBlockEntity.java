package com.maciej916.indreb.common.entity.block;

import com.maciej916.indreb.common.energy.impl.BasicEnergyStorage;
import com.maciej916.indreb.common.energy.interfaces.IEnergy;
import com.maciej916.indreb.common.entity.slot.IndRebSlot;
import com.maciej916.indreb.common.entity.slot.SlotItemHandlerDisabled;
import com.maciej916.indreb.common.entity.slot.SlotItemHandlerOutput;
import com.maciej916.indreb.common.enums.EnergyTier;
import com.maciej916.indreb.common.enums.EnergyType;
import com.maciej916.indreb.common.enums.InventorySlotType;
import com.maciej916.indreb.common.enums.UpgradeType;
import com.maciej916.indreb.common.interfaces.block.IStateActive;
import com.maciej916.indreb.common.interfaces.entity.ICooldown;
import com.maciej916.indreb.common.interfaces.entity.IElectricSlot;
import com.maciej916.indreb.common.interfaces.entity.IExpCollector;
import com.maciej916.indreb.common.interfaces.entity.IHasSlot;
import com.maciej916.indreb.common.interfaces.entity.ISupportUpgrades;
import com.maciej916.indreb.common.interfaces.entity.ITileSound;
import com.maciej916.indreb.common.item.impl.upgrade.ItemUpgrade;
import com.maciej916.indreb.common.network.ModNetworking;
import com.maciej916.indreb.common.network.packet.PacketExperience;
import com.maciej916.indreb.common.registries.ModCapabilities;
import com.maciej916.indreb.common.registries.ModTags;
import com.maciej916.indreb.common.util.CapabilityUtil;
import com.maciej916.indreb.common.util.Constants;
import com.maciej916.indreb.common.util.SoundHandler;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Map.Entry;
import java.util.stream.Stream;
import javax.annotation.Nonnull;
import javax.annotation.Nullable;
import net.minecraft.client.Minecraft;
import net.minecraft.client.resources.sounds.SoundInstance;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.NonNullList;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.Connection;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.TagKey;
import net.minecraft.world.Containers;
import net.minecraft.world.entity.ExperienceOrb;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.common.capabilities.Capability;
import net.minecraftforge.common.util.LazyOptional;
import net.minecraftforge.fluids.FluidStack;
import net.minecraftforge.fluids.capability.CapabilityFluidHandler;
import net.minecraftforge.fluids.capability.IFluidHandler;
import net.minecraftforge.fluids.capability.IFluidHandler.FluidAction;
import net.minecraftforge.items.CapabilityItemHandler;
import net.minecraftforge.items.IItemHandler;
import net.minecraftforge.items.ItemStackHandler;
import net.minecraftforge.items.SlotItemHandler;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.tags.IReverseTag;
import org.jetbrains.annotations.NotNull;

public class IndRebBlockEntity extends BlockEntity implements IHasSlot {
   private ItemStackHandler stackHandler;
   private ArrayList<IndRebSlot> item = new ArrayList<>();
   private final ArrayList<SlotItemHandler> itemHandlers = new ArrayList<>();
   private ArrayList<IElectricSlot> electricSlot = new ArrayList<>();
   private BasicEnergyStorage energyStorage;
   private final LazyOptional<IEnergy> energy = LazyOptional.of(() -> this.energyStorage);
   private ItemStackHandler batteryHandler;
   private final ArrayList<ElectricSlotHandler> batteryHandlers = new ArrayList<>();
   private final ArrayList<IElectricSlot> upgradeSlot = new ArrayList<>();
   private ItemStackHandler upgradesHandler;
   private final ArrayList<UpgradeSlotHandler> upgradeHandlers = new ArrayList<>();
   private Block block;
   protected int tickCounter = 0;
   private int cooldown = 0;
   private boolean invertRedstone = false;
   protected boolean isActivate;
   protected boolean hasCooldown;
   protected boolean hasInventory = false;
   protected boolean hasEnergy = false;
   protected boolean hasBattery = false;
   protected boolean hasSound = false;
   protected boolean hasExp = false;
   protected boolean hasUpgrades = false;
   private SoundEvent soundEvent = null;
   private SoundInstance activeSound;
   private final Map<ResourceLocation, Integer> recipesUsed = new HashMap<>();
   float speedFactor = 1.0F;
   float energyUsageFactor = 1.0F;

   public IndRebBlockEntity(BlockEntityType<?> pType, BlockPos pWorldPosition, BlockState pBlockState) {
      super(pType, pWorldPosition, pBlockState);
      this.init();
   }

   public Block getBlock() {
      return this.block;
   }

   public boolean hasBattery() {
      return this.hasBattery;
   }

   public boolean hasEnergy() {
      return this.hasEnergy;
   }

   public boolean hasUpgrades() {
      return this.hasUpgrades;
   }

   public void init() {
      this.block = this.m_58900_().m_60734_();
      this.setSupportedTypes();
      this.initSlots();
      if (this.hasSound) {
         this.soundEvent = ((ITileSound)this).getSoundEvent();
      }

      if (this.hasUpgrades) {
         this.initUpgradeHandler();
      }
   }

   private void setSupportedTypes() {
      this.isActivate = this.block instanceof IStateActive;
      this.hasCooldown = this instanceof ICooldown;
      this.hasSound = this instanceof ITileSound;
      this.hasExp = this instanceof IExpCollector;
      this.hasUpgrades = this instanceof ISupportUpgrades;
   }

   public void updateBlockState() {
      if (this.f_58857_ != null) {
         this.m_6596_();
         this.f_58857_.m_46597_(this.m_58899_(), this.m_58900_());
         this.f_58857_.m_7260_(this.m_58899_(), this.m_58900_(), this.m_58900_(), 2);
      }
   }

   public void tickServer(BlockState state) {
      if (this.tickCounter == 20) {
         this.tickCounter = 0;
      } else {
         this.tickCounter++;
      }

      if (this.hasCooldown && this.tickCounter == 20 && this.cooldown > 0) {
         this.cooldown--;
         this.updateBlockState();
      }

      if (this.hasUpgrades()) {
         this.tickUpgrades(state);
      }

      this.tickOperate(state);
   }

   public void tickOperate(BlockState state) {
   }

   public void tickUpgrades(BlockState state) {
      int countSpeed = 0;
      int countEnergyUsage = 0;
      int countEnergyStorage = 0;
      int countTransformer = 0;
      this.invertRedstone = false;

      for (int i = 0; i < this.upgradesHandler.getSlots(); i++) {
         ItemStack stack = this.upgradesHandler.getStackInSlot(i);
         CompoundTag tag = stack.m_41784_();
         if (!stack.m_41619_()) {
            Item energyStorageAdd = stack.m_41720_();
            if (energyStorageAdd instanceof ItemUpgrade) {
               ItemUpgrade itemUpgrade = (ItemUpgrade)energyStorageAdd;
               if (itemUpgrade.getUpgradeType() == UpgradeType.OVERCLOCKER) {
                  countSpeed += stack.m_41613_();
                  countEnergyUsage += stack.m_41613_();
               }

               if (itemUpgrade.getUpgradeType() == UpgradeType.ENERGY_STORAGE) {
                  countEnergyStorage += stack.m_41613_();
               }

               if (itemUpgrade.getUpgradeType() == UpgradeType.TRANSFORMER) {
                  countTransformer += stack.m_41613_();
               }

               if (itemUpgrade.getUpgradeType() == UpgradeType.REDSTONE_SIGNAL_INVERTER && !this.invertRedstone) {
                  this.invertRedstone = true;
               }

               if ((
                     itemUpgrade.getUpgradeType() == UpgradeType.PULLING
                        || itemUpgrade.getUpgradeType() == UpgradeType.EJECTOR
                        || itemUpgrade.getUpgradeType() == UpgradeType.FLUID_EJECTOR
                        || itemUpgrade.getUpgradeType() == UpgradeType.FLUID_PULLING
                  )
                  && this.f_58857_.m_46467_() % 5L == 0L) {
                  int direction = tag.m_128431_().contains("Direction") ? tag.m_128451_("Direction") : -1;
                  ArrayList<Direction> directions = new ArrayList<>();
                  if (direction == -1) {
                     directions.addAll(Arrays.stream(Constants.DIRECTIONS).toList());
                  } else {
                     directions.add(Direction.m_122376_(direction));
                  }

                  switch (itemUpgrade.getUpgradeType()) {
                     case PULLING:
                        this.pullItems(directions, stack.m_41613_());
                        break;
                     case EJECTOR:
                        this.ejectItems(directions, stack.m_41613_());
                        break;
                     case FLUID_PULLING:
                        this.pullFluids(directions, stack.m_41613_());
                        break;
                     case FLUID_EJECTOR:
                        this.ejectFluids(directions, stack.m_41613_());
                  }
               }
            }
         }
      }

      double speedFactor = Math.pow(0.7, (double)countSpeed);
      double energyUsageFactor = Math.pow(1.6, (double)countEnergyUsage);
      double energyStorageAdd = (double)(countEnergyStorage * 10000);
      this.speedFactor = (float)speedFactor;
      this.energyUsageFactor = (float)energyUsageFactor;
      double calculateEnergy = (double)this.energyStorage.origEnergy * energyUsageFactor + energyStorageAdd;
      int newEnergy = calculateEnergy < 2.147483647E9 ? (int)calculateEnergy : Integer.MAX_VALUE;
      this.energyStorage.setMaxEnergy(newEnergy);
      int newTier = this.energyStorage.origTier.getLvl() + countTransformer;
      this.energyStorage.setEnergyTier(newTier > 5 ? EnergyTier.ULTRA : EnergyTier.getTierFromLvl(newTier));
   }

   public void pullItems(ArrayList<Direction> directions, int count) {
      for (Direction dir : directions) {
         IItemHandler myHandler = (IItemHandler)CapabilityUtil.getCapabilityHelper(this, CapabilityItemHandler.ITEM_HANDLER_CAPABILITY, dir).getValue();
         if (myHandler != null) {
            BlockEntity blockEntity = this.f_58857_.m_7702_(this.m_58899_().m_142300_(dir));
            if (blockEntity != null) {
               IItemHandler otherHandler = (IItemHandler)CapabilityUtil.getCapabilityHelper(
                     blockEntity, CapabilityItemHandler.ITEM_HANDLER_CAPABILITY, dir.m_122424_()
                  )
                  .getValue();
               if (otherHandler != null) {
                  for (int i = 0; i < otherHandler.getSlots(); i++) {
                     int amount = Math.min(otherHandler.getStackInSlot(i).m_41613_(), count);
                     ItemStack extractItem = otherHandler.extractItem(i, amount, true);
                     boolean found = false;
                     if (!extractItem.m_41619_()) {
                        for (int j = 0; j < myHandler.getSlots(); j++) {
                           ItemStack insertItem = myHandler.insertItem(j, extractItem, true);
                           if (insertItem.m_41619_()) {
                              otherHandler.extractItem(i, amount, false);
                              myHandler.insertItem(j, extractItem, false);
                              found = true;
                              break;
                           }
                        }
                     }

                     if (found) {
                        break;
                     }
                  }
               }
            }
         }
      }
   }

   public void ejectItems(ArrayList<Direction> directions, int count) {
      for (Direction dir : directions) {
         IItemHandler myHandler = (IItemHandler)CapabilityUtil.getCapabilityHelper(this, CapabilityItemHandler.ITEM_HANDLER_CAPABILITY, dir).getValue();
         if (myHandler != null) {
            BlockEntity blockEntity = this.f_58857_.m_7702_(this.m_58899_().m_142300_(dir));
            if (blockEntity != null) {
               IItemHandler otherHandler = (IItemHandler)CapabilityUtil.getCapabilityHelper(
                     blockEntity, CapabilityItemHandler.ITEM_HANDLER_CAPABILITY, dir.m_122424_()
                  )
                  .getValue();
               if (otherHandler != null) {
                  for (int i = 0; i < myHandler.getSlots(); i++) {
                     int amount = Math.min(myHandler.getStackInSlot(i).m_41613_(), count);
                     ItemStack extractItem = myHandler.extractItem(i, amount, true);
                     boolean found = false;
                     if (!extractItem.m_41619_()) {
                        for (int j = 0; j < otherHandler.getSlots(); j++) {
                           ItemStack insertItem = otherHandler.insertItem(j, extractItem, true);
                           if (insertItem.m_41619_()) {
                              myHandler.extractItem(i, amount, false);
                              otherHandler.insertItem(j, extractItem, false);
                              found = true;
                              break;
                           }
                        }
                     }

                     if (found) {
                        break;
                     }
                  }
               }
            }
         }
      }
   }

   public void pullFluids(ArrayList<Direction> directions, int count) {
      for (Direction dir : directions) {
         IFluidHandler myHandler = (IFluidHandler)CapabilityUtil.getCapabilityHelper(this, CapabilityFluidHandler.FLUID_HANDLER_CAPABILITY, dir).getValue();
         if (myHandler != null) {
            BlockEntity blockEntity = this.f_58857_.m_7702_(this.m_58899_().m_142300_(dir));
            if (blockEntity != null) {
               IFluidHandler otherHandler = (IFluidHandler)CapabilityUtil.getCapabilityHelper(
                     blockEntity, CapabilityFluidHandler.FLUID_HANDLER_CAPABILITY, dir.m_122424_()
                  )
                  .getValue();
               if (otherHandler != null) {
                  for (int i = 0; i < otherHandler.getTanks(); i++) {
                     FluidStack stack = otherHandler.getFluidInTank(i);
                     if (!stack.isEmpty()) {
                        stack.setAmount(Math.min(stack.getAmount(), 100 * count));
                        FluidStack extractFluid = otherHandler.drain(stack, FluidAction.SIMULATE);
                        boolean found = false;
                        if (!extractFluid.isEmpty()) {
                           for (int j = 0; j < myHandler.getTanks(); j++) {
                              if (myHandler.isFluidValid(j, extractFluid)) {
                                 int insertAmount = myHandler.fill(stack, FluidAction.SIMULATE);
                                 if (insertAmount > 0) {
                                    extractFluid.setAmount(insertAmount);
                                    otherHandler.drain(extractFluid, FluidAction.EXECUTE);
                                    myHandler.fill(extractFluid, FluidAction.EXECUTE);
                                    found = true;
                                    break;
                                 }
                              }
                           }
                        }

                        if (found) {
                           break;
                        }
                     }
                  }
               }
            }
         }
      }
   }

   public void ejectFluids(ArrayList<Direction> directions, int count) {
      for (Direction dir : directions) {
         IFluidHandler myHandler = (IFluidHandler)CapabilityUtil.getCapabilityHelper(this, CapabilityFluidHandler.FLUID_HANDLER_CAPABILITY, dir).getValue();
         if (myHandler != null) {
            BlockEntity blockEntity = this.f_58857_.m_7702_(this.m_58899_().m_142300_(dir));
            if (blockEntity != null) {
               IFluidHandler otherHandler = (IFluidHandler)CapabilityUtil.getCapabilityHelper(
                     blockEntity, CapabilityFluidHandler.FLUID_HANDLER_CAPABILITY, dir.m_122424_()
                  )
                  .getValue();
               if (otherHandler != null) {
                  for (int i = 0; i < myHandler.getTanks(); i++) {
                     FluidStack stack = myHandler.getFluidInTank(i);
                     if (!stack.isEmpty()) {
                        stack.setAmount(Math.min(stack.getAmount(), 100 * count));
                        FluidStack extractFluid = myHandler.drain(stack, FluidAction.SIMULATE);
                        boolean found = false;
                        if (!extractFluid.isEmpty()) {
                           for (int j = 0; j < otherHandler.getTanks(); j++) {
                              if (otherHandler.isFluidValid(j, extractFluid)) {
                                 int insertAmount = otherHandler.fill(stack, FluidAction.SIMULATE);
                                 if (insertAmount > 0) {
                                    extractFluid.setAmount(insertAmount);
                                    myHandler.drain(extractFluid, FluidAction.EXECUTE);
                                    otherHandler.fill(extractFluid, FluidAction.EXECUTE);
                                    found = true;
                                    break;
                                 }
                              }
                           }
                        }

                        if (found) {
                           break;
                        }
                     }
                  }
               }
            }
         }
      }
   }

   public void tickClient(BlockState state) {
      if (this.hasSound) {
         this.handleSound();
      }
   }

   public void m_7651_() {
      super.m_7651_();
      if (this.hasSound) {
         this.handleSound();
      }

      if (this.hasEnergy) {
         this.energy.invalidate();
      }
   }

   public void initSlots() {
      ArrayList<IndRebSlot> slots = this.addInventorySlot(new ArrayList<>());
      if (slots.size() > 0) {
         this.initStackHandler(slots);
         this.hasInventory = true;
      }
   }

   public ArrayList<IndRebSlot> addInventorySlot(ArrayList<IndRebSlot> slots) {
      return slots;
   }

   public boolean isItemValidForSlot(int slot, @Nonnull ItemStack stack) {
      return true;
   }

   @Nullable
   public ItemStack insertItemForSlot(int slot, @Nonnull ItemStack stack, boolean simulate) {
      return null;
   }

   public void initStackHandler(ArrayList<IndRebSlot> slots) {
      this.item = slots;
      this.stackHandler = new ItemStackHandler(slots.size()) {
         public boolean isItemValid(int slot, @Nonnull ItemStack stack) {
            return IndRebBlockEntity.this.isItemValidForSlot(slot, stack);
         }

         @Nonnull
         public ItemStack insertItem(int slot, @Nonnull ItemStack stack, boolean simulate) {
            ItemStack returnedStack = IndRebBlockEntity.this.insertItemForSlot(slot, stack, simulate);
            return Objects.requireNonNullElseGet(returnedStack, () -> super.insertItem(slot, stack, simulate));
         }

         protected void onContentsChanged(int slot) {
            super.onContentsChanged(slot);
            IndRebBlockEntity.this.m_6596_();
         }
      };
      slots.forEach(sl -> {
         if (sl.getInventorySlotType() == InventorySlotType.OUTPUT) {
            this.itemHandlers.add(new SlotItemHandlerOutput(this, this.stackHandler, sl.getSlotId(), sl.getXPosition(), sl.getYPosition()));
         } else if (sl.getInventorySlotType() == InventorySlotType.DISABLED) {
            this.itemHandlers.add(new SlotItemHandlerDisabled(this.stackHandler, sl.getSlotId(), sl.getXPosition(), sl.getYPosition()));
         } else {
            this.itemHandlers.add(new SlotItemHandler(this.stackHandler, sl.getSlotId(), sl.getXPosition(), sl.getYPosition()));
         }
      });
   }

   public ArrayList<IndRebSlot> getItem() {
      return this.item;
   }

   @NotNull
   public ItemStackHandler getStackHandler() {
      return this.stackHandler;
   }

   public ArrayList<SlotItemHandler> getItemHandlers() {
      return this.itemHandlers;
   }

   public void initBatterySlots() {
      ArrayList<IElectricSlot> slots = this.addBatterySlot(new ArrayList<>());
      if (slots.size() > 0) {
         this.initBatteryStackHandler(slots);
         this.hasBattery = true;
      }
   }

   public ArrayList<IElectricSlot> addBatterySlot(ArrayList<IElectricSlot> slots) {
      return slots;
   }

   public void initBatteryStackHandler(ArrayList<IElectricSlot> slots) {
      this.electricSlot = slots;
      this.batteryHandler = new ItemStackHandler(slots.size()) {
         public boolean isItemValid(int slot, @Nonnull ItemStack stack) {
            return ForgeRegistries.ITEMS
               .tags()
               .getReverseTag(stack.m_41720_())
               .<Stream>map(IReverseTag::getTagKeys)
               .map(tagKeyStream -> tagKeyStream.map(TagKey::f_203868_).toList())
               .orElse(new ArrayList())
               .contains(ModTags.ELECTRICS_RES);
         }

         protected void onContentsChanged(int slot) {
            super.onContentsChanged(slot);
            IndRebBlockEntity.this.m_6596_();
         }
      };
      slots.forEach(
         sl -> this.batteryHandlers
               .add(
                  new ElectricSlotHandler(
                     this.batteryHandler, sl.getSlotId(), sl.getXPosition(), sl.getYPosition(), sl.isCharging(), sl.getInventorySlotType(), this.energyStorage
                  )
               )
      );
   }

   public ItemStackHandler getBatteryHandler() {
      return this.batteryHandler;
   }

   public ArrayList<ElectricSlotHandler> getBatteryHandlers() {
      return this.batteryHandlers;
   }

   public ArrayList<IElectricSlot> getElectricSlot() {
      return this.electricSlot;
   }

   public boolean canExtractEnergyDir(Direction side) {
      return false;
   }

   public boolean canReceiveEnergyDir(Direction side) {
      return false;
   }

   public int customEnergyReceiveTick() {
      return -1;
   }

   public int customEnergyExtractTick() {
      return -1;
   }

   public void createEnergyStorage(int energyStored, int maxEnergy, EnergyType energyType, EnergyTier energyTier) {
      this.energyStorage = new BasicEnergyStorage(energyStored, maxEnergy, energyType, energyTier) {
         public boolean canExtractEnergy(Direction side) {
            return IndRebBlockEntity.this.canExtractEnergyDir(side);
         }

         public boolean canReceiveEnergy(Direction side) {
            return IndRebBlockEntity.this.canReceiveEnergyDir(side);
         }

         public int maxReceiveTick() {
            int customReceive = IndRebBlockEntity.this.customEnergyReceiveTick();
            return customReceive == -1 ? super.maxReceiveTick() : customReceive;
         }

         public int maxExtractTick() {
            int customExtract = IndRebBlockEntity.this.customEnergyExtractTick();
            return customExtract == -1 ? super.maxExtractTick() : customExtract;
         }

         public void updated() {
            IndRebBlockEntity.this.updateBlockState();
         }
      };
      this.hasEnergy = true;
      this.initBatterySlots();
   }

   public BasicEnergyStorage getEnergyStorage() {
      return this.energyStorage;
   }

   public float getSpeedFactor() {
      return this.speedFactor;
   }

   public float getEnergyUsageFactor() {
      return this.energyUsageFactor;
   }

   public List<UpgradeType> getSupportedUpgrades() {
      return new ArrayList<>();
   }

   public void initUpgradeHandler() {
      this.upgradesHandler = new ItemStackHandler(4) {
         public boolean isItemValid(int slot, @Nonnull ItemStack stack) {
            return stack.m_41720_() instanceof ItemUpgrade itemUpgrade
               ? IndRebBlockEntity.this.getSupportedUpgrades().contains(itemUpgrade.getUpgradeType())
               : false;
         }

         protected void onContentsChanged(int slot) {
            super.onContentsChanged(slot);
            IndRebBlockEntity.this.m_6596_();
         }
      };

      for (int i = 0; i < 4; i++) {
         this.upgradeHandlers.add(new UpgradeSlotHandler(this.upgradesHandler, i, 178, 9 + i * 18, this.getSupportedUpgrades()));
      }
   }

   public ArrayList<UpgradeSlotHandler> getUpgradeHandlers() {
      return this.upgradeHandlers;
   }

   public int getTotalMachineSlotCount() {
      return this.itemHandlers.size() + this.batteryHandlers.size() + this.upgradeHandlers.size();
   }

   public int getRedstonePower() {
      if (this.f_58857_ == null) {
         return 0;
      } else {
         int power = this.f_58857_.m_46751_(this.m_58899_());
         return this.invertRedstone ? 15 - power : power;
      }
   }

   public int getCooldown() {
      return this.cooldown;
   }

   public void setCooldown(int time) {
      this.cooldown = time;
   }

   protected boolean getActive() {
      return this.isActivate ? ((IStateActive)this.block).isActive(this.m_58900_()) : false;
   }

   public boolean setActive(boolean active) {
      if (this.isActivate) {
         assert this.f_58857_ != null;

         if (this.getActive() != active) {
            BlockState state = ((IStateActive)this.block).setActive(this.m_58900_(), active);
            this.f_58857_.m_46597_(this.m_58899_(), state);
            return true;
         }
      }

      return false;
   }

   protected boolean canPlaySound() {
      return this.getActive();
   }

   private void handleSound() {
      if (this.hasSound) {
         if (this.canPlaySound() && !this.m_58901_()) {
            if (this.tickCounter > 0) {
               return;
            }

            if (this.activeSound == null || !Minecraft.m_91087_().m_91106_().m_120403_(this.activeSound)) {
               this.activeSound = SoundHandler.startTileSound(this.soundEvent, SoundSource.BLOCKS, 1.0F, this.m_58899_());
            }
         } else if (this.activeSound != null) {
            SoundHandler.stopTileSound(this.m_58899_());
            this.activeSound = null;
         }
      }
   }

   public Runnable collectExp() {
      return () -> ModNetworking.INSTANCE.sendToServer(new PacketExperience(this.m_58899_()));
   }

   public float getExperience(Recipe<?> recipe) {
      return 0.0F;
   }

   public void collectExp(Player player) {
      List<Recipe<?>> list = new ArrayList<>();

      for (Entry<ResourceLocation, Integer> entry : this.recipesUsed.entrySet()) {
         player.f_19853_.m_7465_().m_44043_(entry.getKey()).ifPresent(recipe -> {
            list.add((Recipe<?>)recipe);
            this.spawnExpOrbs(player, entry.getValue(), this.getExperience((Recipe<?>)recipe));
         });
      }

      player.m_7281_(list);
      this.recipesUsed.clear();
   }

   public void setRecipeUsed(@Nullable Recipe<?> recipe) {
      if (recipe != null) {
         this.recipesUsed.compute(recipe.m_6423_(), (key, val) -> 1 + (val == null ? 0 : val));
      }
   }

   private void spawnExpOrbs(Player player, int entry, float experience) {
      if (experience == 0.0F) {
         entry = 0;
      } else if (experience < 1.0F) {
         int i = (int)Math.floor((double)((float)entry * experience));
         if ((double)i < Math.ceil((double)((float)entry * experience)) && Math.random() < (double)((float)entry * experience - (float)i)) {
            i++;
         }

         entry = i;
      }

      while (entry > 0) {
         int j = ExperienceOrb.m_20782_(entry);
         entry -= j;
         this.f_58857_.m_7967_(new ExperienceOrb(this.f_58857_, player.m_20185_(), player.m_20186_() + 0.5, player.m_20189_() + 0.5, j));
      }
   }

   public void onPlace() {
   }

   public void onBreak() {
      NonNullList<ItemStack> stacks = NonNullList.m_122779_();
      if (this.hasInventory) {
         for (int slot = 0; slot < this.stackHandler.getSlots(); slot++) {
            if (this.item.get(slot).getInventorySlotType() != InventorySlotType.DISABLED) {
               stacks.add(this.stackHandler.getStackInSlot(slot));
            }
         }
      }

      if (this.hasBattery) {
         for (int slotx = 0; slotx < this.batteryHandler.getSlots(); slotx++) {
            stacks.add(this.batteryHandler.getStackInSlot(slotx));
         }
      }

      if (this.hasUpgrades) {
         for (int slotx = 0; slotx < this.upgradesHandler.getSlots(); slotx++) {
            stacks.add(this.upgradesHandler.getStackInSlot(slotx));
         }
      }

      Containers.m_19010_(this.m_58904_(), this.m_58899_(), stacks);
   }

   @Nonnull
   public <T> LazyOptional<T> getCapability(@Nonnull Capability<T> cap, @Nullable Direction side) {
      return this.hasEnergy && cap == ModCapabilities.ENERGY ? this.energy.cast() : super.getCapability(cap, side);
   }

   public void handleUpdateTag(CompoundTag tag) {
      this.m_142466_(tag);
   }

   public CompoundTag m_5995_() {
      return this.save(new CompoundTag());
   }

   @Nullable
   public ClientboundBlockEntityDataPacket getUpdatePacket() {
      return ClientboundBlockEntityDataPacket.m_195640_(this);
   }

   public void onDataPacket(Connection net, ClientboundBlockEntityDataPacket pkt) {
      if (pkt.m_131708_() != null) {
         this.m_142466_(pkt.m_131708_());
      }
   }

   public void m_142466_(CompoundTag tag) {
      super.m_142466_(tag);
      if (this.hasInventory) {
         this.stackHandler.deserializeNBT(tag.m_128469_("inventory"));
      }

      if (this.hasBattery) {
         this.batteryHandler.deserializeNBT(tag.m_128469_("battery"));
      }

      if (this.hasUpgrades) {
         this.upgradesHandler.deserializeNBT(tag.m_128469_("upgrade"));
      }

      if (this.hasEnergy) {
         this.energyStorage.setEnergy(tag.m_128451_("energy"));
      }

      if (this.hasCooldown) {
         this.cooldown = tag.m_128451_("cooldown");
      }

      if (this.hasExp) {
         tag.m_128376_("RecipesUsedSize", (short)this.recipesUsed.size());
         int i = 0;

         for (Entry<ResourceLocation, Integer> entry : this.recipesUsed.entrySet()) {
            tag.m_128359_("RecipeLocation" + i, entry.getKey().toString());
            tag.m_128405_("RecipeAmount" + i, entry.getValue());
            i++;
         }
      }
   }

   public CompoundTag save(CompoundTag tag) {
      if (this.hasInventory) {
         tag.m_128365_("inventory", this.stackHandler.serializeNBT());
      }

      if (this.hasBattery) {
         tag.m_128365_("battery", this.batteryHandler.serializeNBT());
      }

      if (this.hasUpgrades) {
         tag.m_128365_("upgrade", this.upgradesHandler.serializeNBT());
      }

      if (this.hasEnergy) {
         tag.m_128405_("energy", this.energyStorage.energyStored());
      }

      if (this.hasCooldown) {
         tag.m_128405_("cooldown", this.cooldown);
      }

      if (this.hasExp) {
         int i = tag.m_128448_("RecipesUsedSize");

         for (int j = 0; j < i; j++) {
            ResourceLocation resourcelocation = new ResourceLocation(tag.m_128461_("RecipeLocation" + j));
            int k = tag.m_128451_("RecipeAmount" + j);
            this.recipesUsed.put(resourcelocation, k);
         }
      }

      return tag;
   }

   protected void m_183515_(CompoundTag tag) {
      this.save(tag);
   }
}
