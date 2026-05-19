package dev.ftb.mods.ftbic.block.entity.generator;

import dev.ftb.mods.ftbic.FTBICConfig;
import net.minecraft.world.level.material.Fluids;
import net.minecraftforge.fluids.FluidStack;
import net.minecraftforge.fluids.IFluidTank;
import net.minecraftforge.fluids.capability.IFluidHandler;
import net.minecraftforge.fluids.capability.IFluidHandler.FluidAction;
import org.jetbrains.annotations.NotNull;

public class GeothermalGeneratorTank implements IFluidHandler, IFluidTank {
   public final GeothermalGeneratorBlockEntity generator;

   public GeothermalGeneratorTank(GeothermalGeneratorBlockEntity g) {
      this.generator = g;
   }

   @NotNull
   public FluidStack getFluid() {
      return this.generator.fluidAmount == 0 ? FluidStack.EMPTY : new FluidStack(Fluids.f_76195_, this.generator.fluidAmount);
   }

   public int getFluidAmount() {
      return this.generator.fluidAmount;
   }

   public int getCapacity() {
      return (Integer)FTBICConfig.MACHINES.GEOTHERMAL_GENERATOR_TANK_SIZE.get();
   }

   public boolean isFluidValid(FluidStack fluidStack) {
      return fluidStack.getFluid() == Fluids.f_76195_;
   }

   public int getTanks() {
      return 1;
   }

   @NotNull
   public FluidStack getFluidInTank(int i) {
      return this.getFluid();
   }

   public int getTankCapacity(int i) {
      return (Integer)FTBICConfig.MACHINES.GEOTHERMAL_GENERATOR_TANK_SIZE.get();
   }

   public boolean isFluidValid(int i, @NotNull FluidStack fluidStack) {
      return this.isFluidValid(fluidStack);
   }

   public int fill(FluidStack resource, FluidAction action) {
      if (!resource.isEmpty() && this.isFluidValid(resource)) {
         int filled = Math.min(this.getCapacity() - this.generator.fluidAmount, resource.getAmount());
         if (filled > 0 && !action.simulate()) {
            this.generator.fluidAmount += filled;
            this.generator.m_6596_();
         }

         return filled;
      } else {
         return 0;
      }
   }

   @NotNull
   public FluidStack drain(int amount, FluidAction action) {
      return FluidStack.EMPTY;
   }

   @NotNull
   public FluidStack drain(FluidStack resource, FluidAction action) {
      return FluidStack.EMPTY;
   }
}
