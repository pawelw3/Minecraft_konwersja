package com.maciej916.indreb.common.block.impl.machines.extruder;

import com.maciej916.indreb.common.block.BlockElectricMachine;
import com.maciej916.indreb.common.config.ServerConfig;
import com.maciej916.indreb.common.enums.EnergyTier;
import com.maciej916.indreb.common.enums.EnumLang;
import com.maciej916.indreb.common.interfaces.block.IHasContainer;
import com.maciej916.indreb.common.interfaces.block.IStateActive;
import com.maciej916.indreb.common.interfaces.block.IStateFacing;
import com.maciej916.indreb.common.util.CapabilityUtil;
import com.maciej916.indreb.common.util.TextComponentUtil;
import java.util.List;
import javax.annotation.Nullable;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.network.chat.TranslatableComponent;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.material.Fluids;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraftforge.fluids.FluidStack;
import net.minecraftforge.fluids.capability.CapabilityFluidHandler;
import net.minecraftforge.fluids.capability.IFluidHandlerItem;
import net.minecraftforge.fluids.capability.IFluidHandler.FluidAction;

public class BlockExtruder extends BlockElectricMachine implements IStateFacing, IHasContainer, IStateActive {
   public BlockExtruder() {
      super(EnergyTier.BASIC, 12, 0);
   }

   public AbstractContainerMenu getContainer(int windowId, Level level, BlockPos pos, Inventory playerInventory, Player playerEntity) {
      return new ContainerExtruder(windowId, level, pos, playerInventory, playerEntity);
   }

   @Nullable
   public BlockEntity m_142194_(BlockPos pos, BlockState state) {
      return new BlockEntityExtruder(pos, state);
   }

   public InteractionResult m_6227_(BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult trace) {
      if (!level.f_46443_ && !player.m_6144_() && level.m_7702_(pos) instanceof BlockEntityExtruder be) {
         ItemStack stack = player.m_21120_(hand);
         if (!stack.m_41619_()) {
            ItemStack newStack = stack.m_41777_();
            newStack.m_41764_(1);
            IFluidHandlerItem cap = (IFluidHandlerItem)CapabilityUtil.getCapabilityHelper(newStack, CapabilityFluidHandler.FLUID_HANDLER_ITEM_CAPABILITY)
               .getValue();
            if (cap != null) {
               FluidStack fluid = cap.getFluidInTank(1);
               if (fluid.getFluid() == Fluids.f_76193_) {
                  if (be.waterStorage.fillFluid(fluid, true) == fluid.getAmount()) {
                     be.waterStorage.fillFluid(fluid, false);
                     cap.drain(fluid.getAmount(), FluidAction.EXECUTE);
                     player.m_36356_(cap.getContainer());
                     stack.m_41774_(1);
                     return InteractionResult.PASS;
                  }
               } else if (fluid.getFluid() == Fluids.f_76195_ && be.lavaStorage.fillFluid(fluid, true) == fluid.getAmount()) {
                  be.lavaStorage.fillFluid(fluid, false);
                  cap.drain(fluid.getAmount(), FluidAction.EXECUTE);
                  player.m_36356_(cap.getContainer());
                  stack.m_41774_(1);
                  return InteractionResult.PASS;
               }
            }
         }
      }

      return super.m_6227_(state, level, pos, player, hand, trace);
   }

   public void m_5871_(ItemStack pStack, @Nullable BlockGetter pLevel, List<Component> pTooltip, TooltipFlag pFlag) {
      super.m_5871_(pStack, pLevel, pTooltip, pFlag);
      pTooltip.add(
         TextComponentUtil.build(
            new MutableComponent[]{
               new TranslatableComponent(EnumLang.ACCEPT.getTranslationKey()).m_130940_(ChatFormatting.GRAY),
               new TranslatableComponent(
                     EnumLang.POWER_TICK.getTranslationKey(),
                     new Object[]{TextComponentUtil.getFormattedEnergyUnit((float)((Integer)ServerConfig.basic_tier_transfer.get()).intValue())}
                  )
                  .m_130940_(this.getEnergyTier().getColor())
            }
         )
      );
      pTooltip.add(
         TextComponentUtil.build(
            new MutableComponent[]{
               new TranslatableComponent(EnumLang.CAPACITY.getTranslationKey()).m_130940_(ChatFormatting.GRAY),
               new TranslatableComponent(
                     EnumLang.POWER.getTranslationKey(),
                     new Object[]{TextComponentUtil.getFormattedEnergyUnit((float)((Integer)ServerConfig.extruder_energy_capacity.get()).intValue())}
                  )
                  .m_130940_(this.getEnergyTier().getColor())
            }
         )
      );
   }
}
