package dev.ftb.mods.ftbic.block.entity;

import dev.ftb.mods.ftbic.FTBICConfig;
import dev.ftb.mods.ftbic.block.ElectricBlock;
import dev.ftb.mods.ftbic.block.ElectricBlockInstance;
import dev.ftb.mods.ftbic.recipe.RecipeCache;
import dev.ftb.mods.ftbic.screen.sync.SyncedData;
import dev.ftb.mods.ftbic.util.EnergyHandler;
import dev.ftb.mods.ftbic.util.OpenMenuFactory;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Random;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicLong;
import net.minecraft.Util;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.network.Connection;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.TranslatableComponent;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.MenuProvider;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import net.minecraftforge.common.capabilities.Capability;
import net.minecraftforge.common.util.LazyOptional;
import net.minecraftforge.items.CapabilityItemHandler;
import net.minecraftforge.items.IItemHandler;
import net.minecraftforge.items.IItemHandlerModifiable;
import net.minecraftforge.items.ItemHandlerHelper;
import net.minecraftforge.network.NetworkHooks;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;

public class ElectricBlockEntity extends BlockEntity implements EnergyHandler, IItemHandlerModifiable {
   private static final AtomicLong ELECTRIC_NETWORK_CHANGES = new AtomicLong(0L);
   public final ElectricBlockInstance electricBlockInstance;
   private boolean changed;
   public double energy;
   public final ItemStack[] inputItems;
   public final ItemStack[] outputItems;
   private LazyOptional<?> thisOptional;
   public boolean active;
   private int changeStateTicks;
   private boolean burnt;
   public double energyCapacity;
   public double maxInputEnergy;
   public boolean autoEject;
   public UUID placerId = Util.f_137441_;
   public String placerName = "";

   public static void electricNetworkUpdated(LevelAccessor level, BlockPos pos) {
      ELECTRIC_NETWORK_CHANGES.incrementAndGet();
   }

   public static long getCurrentElectricNetwork(LevelAccessor level, BlockPos pos) {
      return ELECTRIC_NETWORK_CHANGES.get();
   }

   public ElectricBlockEntity(ElectricBlockInstance type, BlockPos pos, BlockState state) {
      super((BlockEntityType)type.blockEntity.get(), pos, state);
      this.electricBlockInstance = type;
      this.changed = false;
      this.energy = 0.0;
      this.inputItems = new ItemStack[type.inputItemCount];
      this.outputItems = new ItemStack[type.outputItemCount];
      Arrays.fill(this.inputItems, ItemStack.f_41583_);
      Arrays.fill(this.outputItems, ItemStack.f_41583_);
      if (this.inputItems.length + this.outputItems.length > 127) {
         throw new RuntimeException("Internal inventory of " + this.m_58903_().getRegistryName() + " too large!");
      } else {
         this.thisOptional = null;
         this.active = false;
         this.changeStateTicks = 0;
         this.burnt = false;
      }
   }

   public void writeData(CompoundTag tag) {
      tag.m_128347_("Energy", this.energy);
      if (this.inputItems.length + this.outputItems.length > 0) {
         ListTag inv = new ListTag();

         for (int slot = 0; slot < this.inputItems.length + this.outputItems.length; slot++) {
            ItemStack stack = this.getStackInSlot(slot);
            if (!stack.m_41619_()) {
               CompoundTag tag1 = stack.serializeNBT();
               tag1.m_128344_("Slot", (byte)slot);
               inv.add(tag1);
            }
         }

         tag.m_128365_("Inventory", inv);
      }

      if (this.burnt) {
         tag.m_128379_("Burnt", true);
      }

      if (!this.placerId.equals(Util.f_137441_)) {
         tag.m_128362_("PlacerId", this.placerId);
         tag.m_128359_("PlacerName", this.placerName);
      }
   }

   public void readData(CompoundTag tag) {
      this.energy = tag.m_128459_("Energy");
      if (this.inputItems.length + this.outputItems.length > 0) {
         Arrays.fill(this.inputItems, ItemStack.f_41583_);
         Arrays.fill(this.outputItems, ItemStack.f_41583_);
         ListTag inv = tag.m_128437_("Inventory", 10);

         for (int i = 0; i < inv.size(); i++) {
            CompoundTag tag1 = inv.m_128728_(i);
            this.setStackInSlot(tag1.m_128445_("Slot"), ItemStack.m_41712_(tag1));
         }
      }

      this.burnt = tag.m_128471_("Burnt");
      if (tag.m_128403_("PlacerId")) {
         this.placerId = tag.m_128342_("PlacerId");
         this.placerName = tag.m_128461_("PlacerName");
      } else {
         this.placerId = Util.f_137441_;
         this.placerName = "";
      }
   }

   public void writeNetData(CompoundTag tag) {
      tag.m_128379_("Burnt", this.burnt);
   }

   public void readNetData(CompoundTag tag) {
      if (tag != null) {
         this.burnt = tag.m_128471_("Burnt");
      }
   }

   public void m_142466_(CompoundTag tag) {
      super.m_142466_(tag);
      this.readData(tag);
      this.initProperties();
      this.upgradesChanged();
   }

   protected void m_183515_(CompoundTag arg) {
      super.m_183515_(arg);
      this.writeData(arg);
   }

   public void handleUpdateTag(CompoundTag tag) {
      this.readNetData(tag);
      this.initProperties();
   }

   public CompoundTag m_5995_() {
      CompoundTag tag = super.m_5995_();
      this.writeNetData(tag);
      return tag;
   }

   public void onDataPacket(Connection net, ClientboundBlockEntityDataPacket pkt) {
      this.readNetData(pkt.m_131708_());
      this.initProperties();
   }

   public ClientboundBlockEntityDataPacket getUpdatePacket() {
      return ClientboundBlockEntityDataPacket.m_195640_(this);
   }

   public void onLoad() {
      this.initProperties();
      if (this.f_58857_ != null && !this.f_58857_.m_5776_()) {
         this.upgradesChanged();
      }

      super.onLoad();
   }

   public LazyOptional<?> getThisOptional() {
      if (this.thisOptional == null) {
         this.thisOptional = LazyOptional.of(() -> this);
      }

      return this.thisOptional;
   }

   public void invalidateCaps() {
      super.invalidateCaps();
      if (this.thisOptional != null) {
         this.thisOptional.invalidate();
         this.thisOptional = null;
      }
   }

   @NotNull
   public <T> LazyOptional<T> getCapability(@NotNull Capability<T> cap, @Nullable Direction side) {
      return cap == CapabilityItemHandler.ITEM_HANDLER_CAPABILITY && this.inputItems.length + this.outputItems.length > 0
         ? this.getThisOptional().cast()
         : super.getCapability(cap, side);
   }

   protected void handleChanges() {
      if (this.changeStateTicks > 0) {
         this.changeStateTicks--;
      }

      if (this.changeStateTicks <= 0) {
         if (!this.isBurnt()) {
            if (this.f_58857_ != null
               && this.electricBlockInstance.canBeActive
               && this.m_58900_().m_60734_() instanceof ElectricBlock
               && (Boolean)this.m_58900_().m_61143_(ElectricBlock.ACTIVE) != this.active
               && !this.f_58857_.m_5776_()) {
               this.f_58857_.m_7731_(this.f_58858_, (BlockState)this.m_58900_().m_61124_(ElectricBlock.ACTIVE, this.active), 3);
               this.m_6596_();
            }

            this.active = false;
         }

         if (this.f_58857_ != null && !this.m_58900_().m_60795_()) {
            this.f_58857_.m_46717_(this.f_58858_, this.m_58900_().m_60734_());
         }

         this.changeStateTicks = (Integer)FTBICConfig.MACHINES.STATE_UPDATE_TICKS.get();
         if (this.changed) {
            this.setChangedNow();
         }
      }
   }

   public void tick() {
      this.handleChanges();
   }

   public void m_6596_() {
      this.changed = true;
   }

   public void setChangedNow() {
      this.changed = false;
      this.f_58857_.m_151543_(this.f_58858_);
   }

   public int getRedstoneOutputSignalEnergyStorage() {
      return Math.round((float)(this.energy / this.energyCapacity * 15.0));
   }

   public final double getEnergyCapacity() {
      return this.energyCapacity;
   }

   public final double getEnergy() {
      return this.energy;
   }

   public final void setEnergyRaw(double e) {
      this.energy = e;
   }

   public InteractionResult rightClick(Player player, InteractionHand hand, BlockHitResult hit) {
      return InteractionResult.SUCCESS;
   }

   public void openMenu(ServerPlayer player, OpenMenuFactory openMenuFactory) {
      NetworkHooks.openGui(player, new MenuProvider() {
         public Component m_5446_() {
            return ElectricBlockEntity.this.createDisplayName();
         }

         public AbstractContainerMenu m_7208_(int id, Inventory playerInv, Player player1) {
            return openMenuFactory.create(id, playerInv);
         }
      }, buf -> this.writeMenu(player, buf));
   }

   public Component createDisplayName() {
      return new TranslatableComponent(this.m_58900_().m_60734_().m_7705_());
   }

   public void writeMenu(ServerPlayer player, FriendlyByteBuf buf) {
      buf.m_130064_(this.f_58858_);
   }

   public boolean isEnergyHandlerInvalid() {
      return this.isBurnt() || this.m_58901_();
   }

   public final double getMaxInputEnergy() {
      return this.maxInputEnergy;
   }

   @Nullable
   public RecipeCache getRecipeCache() {
      return this.f_58857_ == null ? null : RecipeCache.get(this.f_58857_);
   }

   public int getSlots() {
      return this.inputItems.length + this.outputItems.length;
   }

   @NotNull
   public ItemStack getStackInSlot(int slot) {
      if (slot < 0 || slot >= this.getSlots()) {
         throw new RuntimeException("Slot " + slot + " not in valid range - [0," + this.getSlots() + ")");
      } else {
         return slot >= this.inputItems.length ? this.outputItems[slot - this.inputItems.length] : this.inputItems[slot];
      }
   }

   public void setStackInSlot(int slot, ItemStack stack) {
      if (slot >= 0 && slot < this.getSlots()) {
         if (slot >= this.inputItems.length) {
            ItemStack prev = this.outputItems[slot - this.inputItems.length];
            this.outputItems[slot - this.inputItems.length] = stack;
            this.inventoryChanged(slot, prev);
         } else {
            ItemStack prev = this.inputItems[slot];
            this.inputItems[slot] = stack;
            this.inventoryChanged(slot, prev);
         }
      } else {
         throw new RuntimeException("Slot " + slot + " not in valid range - [0," + this.getSlots() + ")");
      }
   }

   @NotNull
   public ItemStack insertItem(int slot, @NotNull ItemStack stack, boolean simulate) {
      if (slot < this.inputItems.length && !stack.m_41619_() && this.isItemValid(slot, stack)) {
         ItemStack existing = this.inputItems[slot];
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
                  ItemStack prev = this.inputItems[slot];
                  this.inputItems[slot] = reachedLimit ? ItemHandlerHelper.copyStackWithSize(stack, limit) : stack;
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
   public ItemStack extractItem(int slot, int amount, boolean simulate) {
      if (slot >= this.inputItems.length && amount > 0) {
         slot -= this.inputItems.length;
         ItemStack existing = this.outputItems[slot];
         if (existing.m_41619_()) {
            return ItemStack.f_41583_;
         } else {
            int toExtract = Math.min(amount, existing.m_41741_());
            if (existing.m_41613_() <= toExtract) {
               if (!simulate) {
                  this.outputItems[slot] = ItemStack.f_41583_;
                  this.inventoryChanged(slot, existing);
                  return existing;
               } else {
                  return existing.m_41777_();
               }
            } else {
               if (!simulate) {
                  this.outputItems[slot] = ItemHandlerHelper.copyStackWithSize(existing, existing.m_41613_() - toExtract);
                  this.inventoryChanged(slot, existing);
               }

               return ItemHandlerHelper.copyStackWithSize(existing, toExtract);
            }
         }
      } else {
         return ItemStack.f_41583_;
      }
   }

   public void inventoryChanged(int slot, @Nullable ItemStack prev) {
      this.m_6596_();
   }

   public void energyChanged(int prev) {
      if (this.energy == 0.0 || prev == 0 || this.energy == this.energyCapacity) {
         this.m_6596_();
      }
   }

   public int getSlotLimit(int slot) {
      return 64;
   }

   public boolean isItemValid(int slot, @NotNull ItemStack stack) {
      return slot < this.inputItems.length;
   }

   public ItemStack addOutputInSlot(int slot, ItemStack stack) {
      if (this.outputItems[slot].m_41619_()) {
         this.outputItems[slot] = stack;
         return ItemStack.f_41583_;
      } else {
         ItemStack existing = this.outputItems[slot];
         int limit = stack.m_41741_();
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
            if (existing.m_41619_()) {
               this.outputItems[slot] = reachedLimit ? ItemHandlerHelper.copyStackWithSize(stack, limit) : stack;
            } else {
               existing.m_41769_(reachedLimit ? limit : stack.m_41613_());
            }

            this.inventoryChanged(slot, existing);
            return reachedLimit ? ItemHandlerHelper.copyStackWithSize(stack, stack.m_41613_() - limit) : ItemStack.f_41583_;
         }
      }
   }

   public ItemStack addOutput(ItemStack stack) {
      if (stack.m_41619_()) {
         return ItemStack.f_41583_;
      } else {
         for (int i = 0; i < this.outputItems.length; i++) {
            if (this.outputItems[i].m_41720_() == stack.m_41720_()) {
               stack = this.addOutputInSlot(i, stack);
               if (stack.m_41619_()) {
                  return ItemStack.f_41583_;
               }
            }
         }

         for (int ix = 0; ix < this.outputItems.length; ix++) {
            if (this.outputItems[ix].m_41619_()) {
               stack = this.addOutputInSlot(ix, stack);
               if (stack.m_41619_()) {
                  return ItemStack.f_41583_;
               }
            }
         }

         return stack;
      }
   }

   public Direction[] getEjectDirections() {
      if (this.electricBlockInstance.facingProperty != BlockStateProperties.f_61374_) {
         return Direction.values();
      } else {
         Direction rot = (Direction)this.m_58900_().m_61143_(BlockStateProperties.f_61374_);
         return new Direction[]{Direction.DOWN, rot.m_122428_(), rot.m_122424_(), rot.m_122427_(), rot, Direction.UP};
      }
   }

   public void shiftInputs() {
      if (this.inputItems.length > 1) {
         List<ItemStack> stacks = new ArrayList<>();

         for (int i = 0; i < this.inputItems.length; i++) {
            if (!this.inputItems[i].m_41619_()) {
               stacks.add(this.inputItems[i]);
               this.inputItems[i] = ItemStack.f_41583_;
            }
         }

         for (ItemStack stack : stacks) {
            ItemHandlerHelper.insertItemStacked(this, stack, false);
         }
      }
   }

   public void ejectOutputItems() {
      if (this.autoEject) {
         Direction[] directions = null;

         for (int i = 0; i < this.outputItems.length; i++) {
            if (!this.outputItems[i].m_41619_()) {
               for (Direction direction : directions == null ? (directions = this.getEjectDirections()) : directions) {
                  BlockEntity entity = this.f_58857_.m_7702_(this.f_58858_.m_142300_(direction));
                  IItemHandler itemHandler = entity == null
                     ? null
                     : (IItemHandler)entity.getCapability(CapabilityItemHandler.ITEM_HANDLER_CAPABILITY, direction.m_122424_()).orElse(null);
                  if (itemHandler != null) {
                     this.outputItems[i] = ItemHandlerHelper.insertItemStacked(itemHandler, this.outputItems[i].m_41777_(), false);
                     if (this.outputItems[i].m_41619_()) {
                        this.outputItems[i] = ItemStack.f_41583_;
                        break;
                     }
                  }
               }
            }
         }
      }
   }

   public void onBroken(Level level, BlockPos pos) {
      for (ItemStack stack : this.inputItems) {
         Block.m_49840_(level, pos, stack);
      }

      for (ItemStack stack : this.outputItems) {
         Block.m_49840_(level, pos, stack);
      }
   }

   public void initProperties() {
      this.energyCapacity = this.electricBlockInstance.energyCapacity;
      this.maxInputEnergy = this.electricBlockInstance.maxEnergyInput;
      this.autoEject = false;
   }

   public void upgradesChanged() {
   }

   public double getTotalPossibleEnergyCapacity() {
      return this.electricBlockInstance.energyCapacity;
   }

   public void addSyncData(SyncedData data) {
      data.addDouble(SyncedData.ENERGY, () -> this.energy);
      data.addDouble(SyncedData.ENERGY_CAPACITY, () -> this.energyCapacity);
   }

   public final boolean canBurn() {
      return this.electricBlockInstance.canBurn;
   }

   public final void setBurnt(boolean b) {
      if (this.burnt != b && !this.f_58857_.m_5776_() && this.canBurn()) {
         this.burnt = b;
         this.m_6596_();
         this.syncBlock();
         electricNetworkUpdated(this.f_58857_, this.f_58858_);
         if (this.burnt) {
            this.f_58857_.m_46796_(1502, this.f_58858_, 0);
            if (this.electricBlockInstance.canBeActive) {
               this.f_58857_.m_7731_(this.f_58858_, (BlockState)this.m_58900_().m_61124_(ElectricBlock.ACTIVE, false), 3);
            }
         }
      }
   }

   public final boolean isBurnt() {
      return this.burnt;
   }

   public void stepOn(ServerPlayer player) {
   }

   @OnlyIn(Dist.CLIENT)
   public void spawnActiveParticles(Level level, double x, double y, double z, BlockState state, Random r) {
   }

   public Direction getFacing(Direction def) {
      if (this.electricBlockInstance.facingProperty == null) {
         return def;
      } else {
         BlockState state = this.m_58900_();
         return state.m_60734_() instanceof ElectricBlock ? (Direction)state.m_61143_(this.electricBlockInstance.facingProperty) : def;
      }
   }

   public void onPlacedBy(@Nullable LivingEntity entity, ItemStack stack) {
      if (this.savePlacer()) {
         if (entity != null) {
            this.placerId = entity.m_142081_();
            this.placerName = entity.m_6302_();
         } else if (!this.f_58857_.m_5776_()) {
            this.f_58857_.m_7471_(this.f_58858_, false);
         }
      }
   }

   public boolean savePlacer() {
      return false;
   }

   public void syncBlock() {
      this.f_58857_.m_7260_(this.f_58858_, this.m_58900_(), this.m_58900_(), 11);
      this.m_6596_();
   }

   public void neighborChanged(BlockPos pos1, Block block1) {
      if (!this.f_58857_.m_8055_(pos1).m_60713_(block1)) {
         electricNetworkUpdated(this.f_58857_, pos1);
      }
   }

   public static <T extends BlockEntity> void ticker(Level level, BlockPos pos, BlockState state, T entity) {
      ((ElectricBlockEntity)entity).tick();
   }
}
