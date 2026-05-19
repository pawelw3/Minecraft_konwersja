package dev.ftb.mods.ftbic.block.entity.machine;

import dev.ftb.mods.ftbic.FTBICConfig;
import dev.ftb.mods.ftbic.block.FTBICBlocks;
import dev.ftb.mods.ftbic.block.FTBICElectricBlocks;
import dev.ftb.mods.ftbic.screen.PumpMenu;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.BucketPickup;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.material.Fluid;
import net.minecraft.world.level.material.Fluids;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraftforge.common.capabilities.Capability;
import net.minecraftforge.common.util.LazyOptional;
import net.minecraftforge.fluids.FluidStack;
import net.minecraftforge.fluids.FluidUtil;
import net.minecraftforge.fluids.IFluidTank;
import net.minecraftforge.fluids.capability.CapabilityFluidHandler;
import net.minecraftforge.fluids.capability.IFluidHandler;
import net.minecraftforge.fluids.capability.IFluidHandler.FluidAction;
import net.minecraftforge.registries.ForgeRegistries;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;

public class PumpBlockEntity extends DiggingBaseBlockEntity implements IFluidHandler, IFluidTank {
   private static final float[] LASER_COLOR = new float[]{0.2F, 0.5F, 1.0F};
   public FluidStack fluidStack = FluidStack.EMPTY;
   public Fluid filter = Fluids.f_76191_;

   public PumpBlockEntity(BlockPos pos, BlockState state) {
      super(FTBICElectricBlocks.PUMP, pos, state);
   }

   @Override
   public void initProperties() {
      super.initProperties();
      this.diggingMineTicks = (Long)FTBICConfig.MACHINES.PUMP_MINE_TICKS.get();
      this.diggingMoveTicks = (Long)FTBICConfig.MACHINES.PUMP_MOVE_TICKS.get();
   }

   @Override
   public void writeData(CompoundTag tag) {
      super.writeData(tag);
      tag.m_128365_("Fluid", this.fluidStack.writeToNBT(new CompoundTag()));
      tag.m_128359_("Filter", this.filter.getRegistryName().toString());
   }

   @Override
   public void readData(CompoundTag tag) {
      super.readData(tag);
      this.fluidStack = FluidStack.loadFluidStackFromNBT(tag.m_128469_("Fluid"));
      this.filter = (Fluid)ForgeRegistries.FLUIDS.getValue(new ResourceLocation(tag.m_128461_("Filter")));
   }

   @Override
   public void readNetData(CompoundTag tag) {
      super.readNetData(tag);
      this.fluidStack = FluidStack.loadFluidStackFromNBT(tag.m_128469_("Fluid"));
      this.filter = (Fluid)ForgeRegistries.FLUIDS.getValue(new ResourceLocation(tag.m_128461_("Filter")));
   }

   @Override
   public void writeNetData(CompoundTag tag) {
      super.writeNetData(tag);
      tag.m_128365_("Fluid", this.fluidStack.writeToNBT(new CompoundTag()));
      tag.m_128359_("Filter", this.filter.getRegistryName().toString());
   }

   @Override
   public boolean isValidBlock(BlockState state, BlockPos pos) {
      return state.m_60767_().m_76332_()
         && state.m_60734_() instanceof BucketPickup
         && (this.filter == Fluids.f_76191_ || this.filter.m_6212_(state.m_60819_().m_76152_()))
         && state.m_60819_().m_76170_();
   }

   @Override
   public void digBlock(BlockState state, BlockPos miningPos, double lx, double ly, double lz) {
      if (state.m_60734_() instanceof BucketPickup bucketPickup && this.fluidStack.getAmount() + 1000 <= this.getCapacity()) {
         FluidStack fluidStack2 = FluidUtil.getFluidContained(bucketPickup.m_142598_(this.f_58857_, miningPos, state)).orElse(FluidStack.EMPTY);
         if (!fluidStack2.isEmpty()) {
            if (this.filter == Fluids.f_76191_) {
               this.filter = fluidStack2.getFluid();
            } else if (this.filter != fluidStack2.getFluid()) {
               return;
            }

            if (this.fluidStack.isEmpty()) {
               this.fluidStack = new FluidStack(this.filter, 1000);
            } else {
               this.fluidStack.setAmount(this.fluidStack.getAmount() + 1000);
            }

            BlockState replaceState = FTBICConfig.MACHINES.PUMP_REPLACE_FLUID_EXFLUID.get()
               ? ((Block)FTBICBlocks.EXFLUID.get()).m_49966_()
               : Blocks.f_50016_.m_49966_();
            this.f_58857_.m_7731_(miningPos, replaceState, 2);
            this.m_6596_();
         }
      }
   }

   @NotNull
   @Override
   public <T> LazyOptional<T> getCapability(@NotNull Capability<T> cap, @Nullable Direction side) {
      return cap == CapabilityFluidHandler.FLUID_HANDLER_CAPABILITY ? this.getThisOptional().cast() : super.getCapability(cap, side);
   }

   @Override
   public InteractionResult rightClick(Player player, InteractionHand hand, BlockHitResult hit) {
      if (!this.f_58857_.m_5776_()) {
         if (player.m_6047_()) {
            this.paused = !this.paused;
            this.syncBlock();
         } else {
            this.openMenu((ServerPlayer)player, (id, inventory) -> new PumpMenu(id, inventory, this));
         }
      }

      return InteractionResult.SUCCESS;
   }

   @Override
   public void writeMenu(ServerPlayer player, FriendlyByteBuf buf) {
      super.writeMenu(player, buf);
      buf.m_130085_(this.filter.getRegistryName());
      this.fluidStack.writeToPacket(buf);
   }

   @Override
   public float[] getLaserColor() {
      return LASER_COLOR;
   }

   @NotNull
   public FluidStack getFluid() {
      return this.fluidStack;
   }

   public int getFluidAmount() {
      return this.fluidStack.getAmount();
   }

   public int getCapacity() {
      return (Integer)FTBICConfig.MACHINES.PUMP_TANK_CAPACITY.get();
   }

   public boolean isFluidValid(FluidStack fluidStack) {
      return false;
   }

   public int getTanks() {
      return 1;
   }

   @NotNull
   public FluidStack getFluidInTank(int i) {
      return this.fluidStack;
   }

   public int getTankCapacity(int i) {
      return (Integer)FTBICConfig.MACHINES.PUMP_TANK_CAPACITY.get();
   }

   public boolean isFluidValid(int i, @NotNull FluidStack fluidStack) {
      return false;
   }

   public int fill(FluidStack fluidStack, FluidAction fluidAction) {
      return 0;
   }

   @NotNull
   public FluidStack drain(FluidStack resource, FluidAction action) {
      return this.f_58857_ != null && !this.f_58857_.m_5776_() && !resource.isEmpty() && resource.isFluidEqual(this.fluidStack)
         ? this.drain(resource.getAmount(), action)
         : FluidStack.EMPTY;
   }

   @NotNull
   public FluidStack drain(int maxDrain, FluidAction action) {
      if (this.f_58857_ != null && !this.f_58857_.m_5776_()) {
         int drained = maxDrain;
         if (this.fluidStack.getAmount() < maxDrain) {
            drained = this.fluidStack.getAmount();
         }

         FluidStack stack = new FluidStack(this.fluidStack, drained);
         if (action.execute() && drained > 0) {
            this.fluidStack.shrink(drained);
            this.m_6596_();
            if (this.fluidStack.isEmpty() && this.paused) {
               this.paused = false;
               this.syncBlock();
            }
         }

         return stack;
      } else {
         return FluidStack.EMPTY;
      }
   }
}
