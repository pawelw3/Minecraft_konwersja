package dev.ftb.mods.ftbic.block.entity.generator;

import dev.ftb.mods.ftbic.FTBICConfig;
import dev.ftb.mods.ftbic.block.FTBICElectricBlocks;
import dev.ftb.mods.ftbic.util.FTBICUtils;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.TranslatableComponent;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;

public class WindMillBlockEntity extends GeneratorBlockEntity {
   private int blocksInRadius = -1;
   public double output = 0.0;

   public WindMillBlockEntity(BlockPos pos, BlockState state) {
      super(FTBICElectricBlocks.WIND_MILL, pos, state);
   }

   @Override
   public void handleGeneration() {
      this.output = 0.0;
      if (this.energy < this.energyCapacity && this.f_58857_.m_45527_(this.f_58858_.m_7494_())) {
         if (this.f_58857_.m_46467_() % 1200L == 0L) {
            this.blocksInRadius = -1;
         }

         if (this.blocksInRadius == -1) {
            this.blocksInRadius = 0;

            for (int x = -5; x <= 5; x++) {
               for (int z = -5; z <= 5; z++) {
                  for (int y = -2; y <= 5; y++) {
                     if ((y > 0 || x != 0 || z != 0) && !this.f_58857_.m_46859_(this.f_58858_.m_142082_(x, y, z))) {
                        this.blocksInRadius++;
                     }
                  }
               }
            }
         }

         int height = this.f_58858_.m_123342_() - this.blocksInRadius;
         if (height < (Integer)FTBICConfig.MACHINES.WIND_MILL_MIN_Y.get()) {
            return;
         }

         if (height > (Integer)FTBICConfig.MACHINES.WIND_MILL_MAX_Y.get()) {
            height = (Integer)FTBICConfig.MACHINES.WIND_MILL_MAX_Y.get();
         }

         this.output = Mth.m_14139_(
            (double)height / (double)((Integer)FTBICConfig.MACHINES.WIND_MILL_MAX_Y.get() - (Integer)FTBICConfig.MACHINES.WIND_MILL_MIN_Y.get()),
            (Double)FTBICConfig.MACHINES.WIND_MILL_MIN_OUTPUT.get(),
            (Double)FTBICConfig.MACHINES.WIND_MILL_MAX_OUTPUT.get()
         );
         if (this.output <= 0.0) {
            return;
         }

         if (this.f_58857_.m_46470_()) {
            this.output = this.output * (Double)FTBICConfig.MACHINES.WIND_MILL_THUNDER_MODIFIER.get();
         } else if (this.f_58857_.m_46471_()) {
            this.output = this.output * (Double)FTBICConfig.MACHINES.WIND_MILL_RAIN_MODIFIER.get();
         }

         this.energy = this.energy + Math.min(this.energyCapacity - this.energy, this.output);
         if (this.energy >= this.energyCapacity) {
            this.m_6596_();
         }
      }
   }

   @Override
   public InteractionResult rightClick(Player player, InteractionHand hand, BlockHitResult hit) {
      if (!this.f_58857_.m_5776_()) {
         player.m_5661_(new TranslatableComponent("ftbic.energy_output", new Object[]{FTBICUtils.formatEnergy(this.output)}), false);
      }

      return InteractionResult.SUCCESS;
   }
}
