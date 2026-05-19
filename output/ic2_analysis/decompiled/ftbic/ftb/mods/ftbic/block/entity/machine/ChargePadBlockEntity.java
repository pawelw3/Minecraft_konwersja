package dev.ftb.mods.ftbic.block.entity.machine;

import dev.ftb.mods.ftbic.block.FTBICElectricBlocks;
import dev.ftb.mods.ftbic.block.entity.ElectricBlockEntity;
import dev.ftb.mods.ftbic.util.EnergyItemHandler;
import java.util.Random;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import net.minecraftforge.items.CapabilityItemHandler;
import net.minecraftforge.items.IItemHandler;

public class ChargePadBlockEntity extends ElectricBlockEntity {
   public ChargePadBlockEntity(BlockPos pos, BlockState state) {
      super(FTBICElectricBlocks.CHARGE_PAD, pos, state);
   }

   @Override
   public void stepOn(ServerPlayer player) {
      if (this.energy > 0.0) {
         IItemHandler handler = (IItemHandler)player.getCapability(CapabilityItemHandler.ITEM_HANDLER_CAPABILITY).orElse(null);
         if (handler != null) {
            for (int i = 0; i < handler.getSlots(); i++) {
               ItemStack stack = handler.getStackInSlot(i);
               Item e = stack.m_41720_();
               if (e instanceof EnergyItemHandler) {
                  EnergyItemHandler energyItemHandler = (EnergyItemHandler)e;
                  if (!energyItemHandler.isCreativeEnergyItem()) {
                     double ex = energyItemHandler.insertEnergy(stack, this.energy, false);
                     if (ex > 0.0) {
                        this.energy -= ex;
                        this.active = true;
                        this.m_6596_();
                        if (this.energy <= 0.0) {
                           break;
                        }
                     }
                  }
               }
            }
         }
      }
   }

   @OnlyIn(Dist.CLIENT)
   @Override
   public void spawnActiveParticles(Level level, double x, double y, double z, BlockState state, Random r) {
      for (int i = 0; i < 5; i++) {
         level.m_7106_(
            DustParticleOptions.f_123656_, x + (double)r.nextFloat(), y + 1.0 + (double)(r.nextFloat() * 2.0F), z + (double)r.nextFloat(), 0.0, 0.0, 0.0
         );
      }
   }
}
