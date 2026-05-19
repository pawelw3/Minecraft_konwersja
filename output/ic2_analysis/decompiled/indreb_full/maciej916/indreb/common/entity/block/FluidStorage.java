package com.maciej916.indreb.common.entity.block;

import java.util.function.Predicate;
import net.minecraftforge.fluids.FluidStack;
import net.minecraftforge.fluids.capability.IFluidHandler.FluidAction;
import net.minecraftforge.fluids.capability.templates.FluidTank;

public class FluidStorage extends FluidTank {
   public FluidStorage(int capacity) {
      super(capacity);
   }

   public FluidStorage(int capacity, Predicate<FluidStack> validator) {
      super(capacity, validator);
   }

   public int fillFluid(FluidStack resource, boolean simulate) {
      int fluidFilled = Math.min(this.capacity - this.fluid.getAmount(), Math.min(this.capacity, resource.getAmount()));
      if (!simulate) {
         this.fill(resource, FluidAction.EXECUTE);
      }

      return fluidFilled;
   }

   public int takeFluid(int amount, boolean simulate) {
      int fluidExtracted = Math.min(this.fluid.getAmount(), amount);
      if (!simulate) {
         this.drain(amount, FluidAction.EXECUTE);
      }

      return fluidExtracted;
   }
}
